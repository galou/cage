# The following commands allow to put pages that are smaller that A5 onto a
# booklet to print on A4 pages both sides.
# By default (i.e. pdfbook without further option), the pages are centered, so that you have to make 4 cuts. With
# these commands, the pages are in one corner.
#
# Adapt to your needs (file names, offsets and page count).
# You can use pdfjam option '--frame true' to add a frame for debugging or cutting.

pdfjam --booklet true --landscape --signature 4 --rotateoversize false --noautoscale true --offset "-9.6mm -6.5mm" --outfile odd.pdf \
	p001.pdf \
	p002.pdf \
	p003.pdf \
	p004.pdf

pdfjam --booklet true --landscape --signature 4 --rotateoversize false --noautoscale true --offset "9.6mm 6.5mm" --outfile even.pdf \
	p001.pdf \
	p002.pdf \
	p003.pdf \
	p004.pdf

pdfseparate odd.pdf odd-%03d.pdf

pdfseparate even.pdf even-%03d.pdf

pdfjoin --outfile autodoc.pdf \
	odd-001.pdf \
	even-002.pdf
