-- Turns one research document into a chapter of the e-book, for
-- scripts/render_epub.py. Run after drop_toc_section.lua.
--
-- The document's # title becomes the chapter heading, with the slug as its
-- identifier, and every other heading moves down one level beneath it. Every
-- other identifier gets a "<slug>--" prefix so thirteen documents can share one
-- book, and links between documents become links within it.
--
-- Web-only blocks are dropped: styles, scripts and the interactive canvas
-- figure, whose print still stands in for it, plus the per-document footer,
-- which the book's title page replaces. The raw-HTML ELI5 card becomes a div.
--
-- Metadata in: epub-chapter (slug), epub-number, epub-chapters (all slugs,
-- comma-separated).

local slug, title_id
local chapters = {}

-- ASCII only: e-reader converters are stricter about identifiers than EPUB 3.
local function anchor(doc, id)
  return doc .. "--" .. id:gsub("[^A-Za-z0-9_.%-]", "")
end

local function prefix(id)
  if id == title_id then
    return slug
  end
  return anchor(slug, id)
end

-- nil means "unlink": the target has no place in the book.
local function retarget(target)
  local fragment = target:match("^#(.+)$")
  if fragment then
    return "#" .. prefix(fragment)
  end
  local doc, rest = target:match("^([%w_]+)%.html(.*)$")
  if not doc then
    return target
  end
  if doc == "index" then
    return nil
  end
  if not chapters[doc] then
    io.stderr:write("warning: " .. slug .. ": link to " .. target .. ", which is not a chapter\n")
    return target
  end
  fragment = rest:match("^#(.+)$")
  return "#" .. (fragment and anchor(doc, fragment) or doc)
end

local function image_block(src, alt)
  return pandoc.Para({ pandoc.Image(alt, src, "", pandoc.Attr("", { "figure" })) })
end

local function html_figures(blocks)
  local stems = {}
  for _, block in ipairs(blocks) do
    if block.t == "RawBlock" and block.format == "html" then
      local src = block.text:match('<img[^>]-src="([^"]+)"')
      if src then
        stems[src:gsub("%.%w+$", "")] = true
      end
    end
  end
  return stems
end

local function file_exists(path)
  local f = io.open(path, "r")
  if f then
    f:close()
  end
  return f ~= nil
end

local function convert_raw(block, shown)
  if block.format == "html" then
    local text = block.text
    if text:find("<style") or text:find("<script") or text:find("<canvas") then
      return {}
    end
    local src = text:match('<img[^>]-src="([^"]+)"')
    if src then
      local alt = text:match('alt="([^"]*)"') or ""
      return { image_block(src, pandoc.Inlines(alt)) }
    end
    io.stderr:write("warning: " .. slug .. ": raw HTML passed through: " .. text:sub(1, 60) .. "\n")
    return { block }
  end
  -- A print-only figure stands in when the web shows no image of it, as for
  -- the interactive canvas; the e-book takes its SVG sibling.
  local pdf = block.text:match("\\includegraphics[^{]*{([^}]+)%.pdf}")
  if pdf and not shown[pdf] then
    if file_exists(pdf .. ".svg") then
      return { image_block(pdf .. ".svg", {}) }
    end
    io.stderr:write("warning: " .. slug .. ": no " .. pdf .. ".svg for the print-only figure\n")
  end
  return {}
end

local function drop_footer(blocks)
  for i = #blocks, 1, -1 do
    if blocks[i].t == "HorizontalRule" then
      local is_footer = false
      for j = i + 1, #blocks do
        blocks[j]:walk({
          Link = function(link)
            is_footer = is_footer or link.target == "index.html"
          end,
        })
      end
      if is_footer then
        for _ = i, #blocks do
          blocks:remove()
        end
      end
      return blocks
    end
  end
  return blocks
end

local function restructure(blocks)
  local shown = html_figures(blocks)
  local out, eli5 = pandoc.Blocks({}), nil
  for _, block in ipairs(blocks) do
    if block.t == "RawBlock" and block.format == "html" and block.text:match('^%s*<aside class="eli5">%s*$') then
      eli5 = pandoc.Blocks({})
    elseif block.t == "RawBlock" and block.format == "html" and block.text:match("^%s*</aside>%s*$") then
      -- The heading leads the card rather than sitting inside it, as in the
      -- PDF, so it stays a section the book can split at and list.
      local heading = eli5[1] and eli5[1].t == "Header" and eli5:remove(1)
      if heading then
        out:insert(heading)
      end
      out:insert(pandoc.Div(eli5, pandoc.Attr("", { "eli5" })))
      eli5 = nil
    else
      local converted = block.t == "RawBlock" and convert_raw(block, shown) or { block }
      local into = eli5 or out
      for _, b in ipairs(converted) do
        into:insert(b)
      end
    end
  end
  return out
end

local function relabel(blocks)
  local function rename(el)
    if el.identifier and el.identifier ~= "" then
      el.identifier = prefix(el.identifier)
      return el
    end
  end
  blocks = blocks:walk({ Block = rename, Inline = rename })
  return blocks:walk({
    Header = function(h)
      h.level = h.level + 1
      return h
    end,
    Link = function(link)
      local target = retarget(link.target)
      if not target then
        return link.content
      end
      link.target = target
      return link
    end,
  })
end

function Pandoc(doc)
  slug = pandoc.utils.stringify(doc.meta["epub-chapter"])
  local number = pandoc.utils.stringify(doc.meta["epub-number"])
  for s in pandoc.utils.stringify(doc.meta["epub-chapters"]):gmatch("[^,]+") do
    chapters[s] = true
  end

  local blocks = drop_footer(doc.blocks)
  local title = blocks:remove(1)
  assert(title.t == "Header" and title.level == 1, slug .. ": expected the document to open with its # title")
  title_id = title.identifier
  local subtitle = blocks[1].t == "Header" and blocks[1].level == 3 and blocks:remove(1)
  if blocks[1].t == "HorizontalRule" then
    blocks:remove(1)
  end

  local label = pandoc.Span("Chapter " .. number, pandoc.Attr("", { "chapter-number" }))
  local head = pandoc.Blocks({
    pandoc.Header(1, { label, pandoc.Space(), table.unpack(title.content) }, pandoc.Attr(slug)),
  })
  if subtitle then
    head:insert(pandoc.Div(pandoc.Para(subtitle.content), pandoc.Attr("", { "subtitle" })))
  end
  head:extend(relabel(restructure(blocks)))
  doc.blocks = head
  return doc
end
