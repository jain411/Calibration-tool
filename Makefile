clean:
	rm -f *~ 
	echo "Cleaning *~ files...."
	rm -rvf `find ./ -name "*~" -print`
	echo "Cleaning .swp files...."
	rm -rvf `find ./ -name "*.swp" -print`
	echo "Cleaning .pyc files...."
	rm -rvf `find ./ -name "*.pyc" -print`

.PHONY: clean 


