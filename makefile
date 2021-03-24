#++++++++++++++++++++++++++++++++++++++++++++++++
#
# Set up this Makefile:
#   Place all image files in a subdirectory.
#   Update all variables in the first section below.
#
# Use this Makefile:
#   Run "make help", or see end of file.
#
# Description of file:
#  Keep the images in lists, one list per format.
#  When compiling into for instance a .dvi file, the target.dvi rule is used.
#    Bibtex and convertion between .eps and .pdf images are handled within this rule.
#    (I found no way to generate multiple rules from a list)
#  Converting from .svg files into .eps or .pdf files are done in their own rules.
#  Some make/shell help is written in the end of this file.
# 
#################################################

# Image sources: Only include the original files (not files created by this script).
IMAGES = logo logo2 # pdfs or svgs
OTHERS = cat.jpg # files without conversion support
NAME = sigbovik-psll # Latex top file (excl .tex)

#################################################
VPATH = img lib
ALL_IMAGES = $(patsubst %,%.pdf,$(IMAGES)) $(OTHERS)
BIB_NAME = $(NAME).bib # including .bib

# When to run bibtex. 0=never, 1=if .bib was changed, 2=always. see help
RUNBIB=0

# Spam filter for latex outputs
# egrep filter was ok, but it was a pain to remove the Fotn shape declaration warnings
# FilterLatex = egrep "Class|Warning|entering|LaTeX2e|Output|Transcript|Document Class|For additional" | egrep -v "Font shape declaration"
FilterLatex = awk '
FilterLatex += /Class/ || (/Warning/ && !/Font shape declaration/) ||
FilterLatex += /Failed/ ||
FilterLatex += /entering/ || /LaTeX2e/ || /Output/ || /Transcript/ ||
FilterLatex += /Document Class/ || /For additional/
FilterLatex += ' # Closing quote of the awk command

NAME := $(strip $(NAME))

LATEX_FLAGS = -halt-on-error

#============== PHONY COMMANDS (except help) ================
default: pdf

pdf: $(NAME).pdf
bib: $(NAME).bbl $(NAME).aux

## Recipies

# Pake pdfs from svgs
%.pdf: %.svg
	@echo "PDF <- SVG $@"
	@inkscape --export-text-to-path --export-type=pdf --export-filename=$@ $<

clean:
	@ rm -vf $(NAME).aux $(NAME).log $(NAME)Notes.bib $(NAME).synctex.gz $(NAME).pdf $(NAME).blg $(NAME).bbl

$(NAME).pdf $(NAME).aux: $(NAME).tex $(BIB_NAME) $(ALL_IMAGES)
	@ if [ $(NAME).tex -nt $(NAME).log ]; then \
	    echo "======= Running pdfLaTeX (for bibtex purpose) ======="; \
	    pdflatex $(NAME).tex | $(FilterLatex); \
	fi;
	@ echo "======= Running BibTeX =======" ;
	@ bibtex $(NAME) ;
	@ echo "======= Running PDFLaTeX ======="
	@ while : ; do\
	    pdflatex $(NAME).tex | $(FilterLatex);\
	    if grep -q "Rerun to get" $(NAME).log; then\
	    echo "======= Rerunning PDFLaTeX =======";\
	    else break; fi;\
	done;

# ===== The bibliography, as a stand-alone command (this is not called normally) =====
$(NAME).bbl: $(NAME).tex $(BIB_NAME)
	@echo "======= Running BibTeX ======="
	@bibtex $(NAME)

#============== PHONY HELP ================
help:
	@echo ""
	@echo "make <cmd> [NAME=<main name>] [RUNBIB=0/1/2]"
	@echo ""
	@echo " <cmd>:"
	@echo "    dvi     - latex: .tex -> .dvi."
	@echo "    dvipdf  - latex + dvipdf: .tex -> .dvi -> .dvi.pdf."
	@echo "    kdvi    - latex + kdvi: .tex -> .dvi, view in KDVI."
	@echo "    dviacro - latex + dvipdf + acroread: .tex -> .dvi -> .dvi.pdf, view in acroread."
	@echo "    pdf     - pdflatex: .tex -> pdf."
	@echo "    acro    - pdflatex + acroread: .tex -> .pdf, view in acroread."
	@echo "    bib     - bibtex: .aux,.bib -> .bbl (independent of RUNBIB)."
	@echo "    clean   - rm *~ *aux *backup *log *toc *bbl *blg *lot *lof."
	@echo "    superclean - clean + rm generated images and dvi/pdf files"
	@echo "    help    - show this message. This is default, if no <cmd> are given."
	@echo ""
	@echo " NAME: optional name of main latex file (excl. \".tex\"). Actual=$(NAME)."
	@echo ""
	@echo " RUNBIB: Decide whether to update the bibliography file or not. Actual=$(RUNBIB)."
	@echo "       =0: Never run bibtex (more then by the bib command)."
	@echo "       =1: Run bibtex if .bib was changed, or .bbl is missing."
	@echo "       =2: Run bibtex every time."
	@echo ""
	@echo " Example (without bibtex): make dviacro NAME=report"
	@echo "  -> latex report.tex; dvipdf report.dvi report.dvi.pdf; acroread report.dvi.pdf"
	@echo " Example (with bibtex): make dviacro NAME=report"
	@echo "  -> latex report.tex; bibtex report; latex report.tex; latex report.tex; dvipdf report.dvi report.dvi.pdf; acroread report.dvi.pdf"
	@echo ""
	@echo " PS. .tex->.dvi can only handle .eps files."
	@echo "     .tex->.pdf can NOT handle .eps files, but e.g. PDF/PNG files."
	@echo "     This makefile will automatically convert from svg images to eps or pdf formats."
	@echo "     This makefile will automatically convert from pdf images to eps formats."
	@echo "     This makefile will automatically convert from eps images to pdf formats."
	@echo "     This makefile has no support for other image formats (which does not mean they cannot be used)."
	@echo ""

# Some shell command syntax (see "man sh", "man test"):
# > for VAR in LIST ; do COMMANDS; done
# > if [ ... ]; then COMMANDS; fi
# > ...: -o = logical OR, -eq = numerical equal, -e = exist, ! = not, -nt = newer than.
#        "A -nt B" = true if file A is newer than file B, or if (only) file B is missing.
#        "A -nt B" = false if file B is not older than file A, or if file A is missing.
#
# The complete make manual: http://www.gnu.org/software/make/manual/