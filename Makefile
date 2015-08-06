all : well_plans.csv

well_plans.csv : easy_well_plans.csv hard_well_plans.csv 
	python3 merge_plans.py $^ > $@


hard_well_plans.csv : easy_well_plans.csv ocr_exclude.txt \
	              $(shell grep ,,False well_plans.csv | \
	        	      grep -oP '(.*)(?=\.pdf)' | \
                              grep -v -f ocr_exclude.txt | \
                              sed -z 's/\n/_text /g') 
	python3 hard_extract.py  $(filter %_text,$^) > $@

easy_well_plans.csv : $(wildcard html/pdf/*.pdfs.html)
	  python3 easy_extract.py $^ > $@


%_text : pdf/%.pdf html/pdf/%.pdfs.html
	mkdir -p $*_images

	for page in `grep -oP '<A name=\K([0-9]+)(?=></a><hr>)' $(word 2, $^)` ; \
	  do pdftoppm -f $$page -l $$page -r 300 $< > $*_images/$$page.ppm ; \
          done

	ocrfeeder-cli -e TESSERACT -f HTML -i \
	  `echo $*_images/*.ppm | sed 's/ / -i /g'` -o $@

	rm -rf $*_images


