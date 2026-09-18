-- Drops the authored "Table of contents" section from HTML output, where the
-- outline sidebar replaces it. The markdown (and so the PDF) keeps it.
--
-- The section runs from its heading through the next horizontal rule, or up
-- to the next heading of the same or higher level.

function Pandoc(doc)
  local blocks, level = pandoc.Blocks({}), nil
  for _, block in ipairs(doc.blocks) do
    if level then
      local rule = block.t == "HorizontalRule"
      if rule or (block.t == "Header" and block.level <= level) then
        level = false
        if not rule then blocks:insert(block) end
      end
    elseif level == nil and block.t == "Header" and block.identifier == "table-of-contents" then
      level = block.level
    else
      blocks:insert(block)
    end
  end
  doc.blocks = blocks
  return doc
end
