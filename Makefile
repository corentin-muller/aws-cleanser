include golang.mk

format:
	gofmt -w .
format_code:
	black .

.PHONY: format

