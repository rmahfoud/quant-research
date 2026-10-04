.PHONY: render-docs epub
render-docs:
	./scripts/render_docs.sh all

epub:
	python3 ./scripts/render_epub.py
