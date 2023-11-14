include golang.mk

format:
	gofmt -w .
format_code:
	black .
qa_check_code:
	flake8 .


.PHONY: format

