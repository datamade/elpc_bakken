well_plans.csv :  
	for file in html/pdf/*.pdfs.html; \
	  do python3 extract.py "$$file"; \
	  done	> $@	
