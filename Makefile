all : foo

well_plans.csv :  
	for file in html/pdf/*.pdfs.html; \
	  do python3 extract.py "$$file"; \
	  done	> $@	

foo : well_plans.csv $(shell grep ,, well_plans.csv | grep -oP '(.*)(?=\.pdf)' | sed -z 's/\n/_text /g')

%_text : pdf/%.pdf html/pdf/%.pdfs.html
	mkdir -p $*_images
	for page in `grep -oP '<A name=\K([0-9]+)(?=></a><hr>)' $(word 2, $^)` ; \
	  do pdftoppm -f $$page -l $$page -r 300 $< > $*_images/$$page.ppm ; \
          done
	ocrfeeder-cli -e TESSERACT -f HTML -i \
	  `echo $*_images/*.ppm | sed 's/ / -i /g'` -o $@
	rm -rf $*_images


