all : foo

well_plans.csv :  
	for file in html/pdf/*.pdfs.html; \
	  do python3 extract.py "$$file"; \
	  done	> $@	

foo : well_plans.csv $(shell grep ,, well_plans.csv | grep -oP '(.*)(?=\.pdf)' | sed -z 's/\n/_extracted /g')

%_extracted : pdfs/%.pdf html/pdf/%.pdfs.html
	mkdir -p $*
	for page in `grep -oP '<A name=\K([0-9]+)(?=></a><hr>)' $(word 2, $^)` ; \
	  do pdftoppm -f $$page -l $$page -r 300 $< > $*/$$page.ppm ; \
          done
	ocrfeeder-cli -e TESSERACT -f HTML \
          $(patsubst %, -i %, $(wildcard $*\/*.ppm)) -o $@
	rm $*/*.ppm


