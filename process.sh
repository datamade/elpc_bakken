for file in pdf/*
do
  pdftohtml "$file" html/"$file".html
done