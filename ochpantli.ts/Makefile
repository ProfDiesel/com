export PATH := $(shell pwd)/node_modules/.bin:$(PATH)

build:
	tsc --build

clean:
	rm -Rf dist coverage
	tsc --build --clean
