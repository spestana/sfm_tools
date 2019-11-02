# get exif lat and lon from DJI images
# derived from https://github.com/dshean/sfm_tools/blob/master/dji_alt_adjust.py by dshean
#
# Currently requires PyExifTool:
# pip install ocrd-pyexiftool
# which in turn, requires that exiftool is installed and available on your $PATH

import exiftool
import pandas as pd
import os, sys, argparse


#-----------------COMMAND LINE ARGUMENTS -------------------#
# Set up argument and error handling
parser = argparse.ArgumentParser(description='Get image locaitons from EXIF data, export to csv')
parser.add_argument('-i','--indir', required=True, help='Directory containing images')
args = parser.parse_args()

# Check to make sure the directory input is valid
if args.indir[-1] != '/' and args.indir[-1] != '\\': 
	inDir = ( args.indir.strip("'").strip('"') + os.sep )
else: 
	inDir = args.indir
try:
	os.path.isdir(inDir)
except FileNotFoundError:
	print('error: input directory provided does not exist or was not found:\n{}'.format(args.indir))
	sys.exit(2)

#-----------------GET METADATA-------------------#
#Returns dictionary with relevant EXIF tags 
def get_metadata(fn, et):
    tags = ['EXIF:GPSLatitude', 'EXIF:GPSLongitude', 'EXIF:GPSLatitudeRef', 'EXIF:GPSLongitudeRef', \
            'EXIF:GPSAltitude', 'EXIF:GPSAltitudeRef', 'XMP:AbsoluteAltitude', 'XMP:RelativeAltitude']
    metadata = et.get_tags(tags, fn)
    #Convert to positive east longitude
    if metadata['EXIF:GPSLongitudeRef'] == "W":
        metadata['EXIF:GPSLongitude'] *= -1
    if metadata['EXIF:GPSLatitudeRef'] == "S":
        metadata['EXIF:GPSLatitude'] *= -1
    return metadata

#-----------------GET LIST OF FILES -------------------#
# Function to find all JPG files in a specified directory
def getListOfFiles(dirName,ext):
    '''Create a list of file names in the given directory with specified file extension.'''
    # https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Only match files with the correct extension
        if '.'+ext == os.path.splitext(entry)[1]:
            # Create full path and add to list
            fullPath = os.path.join(dirName, entry)
            allFiles.append(fullPath)       
    return allFiles

#-----------------MAIN ROUTINE-------------------#
def main():
	#Start subprocess with exiftool
	print('Starting exiftool process')
	et = exiftool.ExifTool() 
	et.start()

	print('Getting list of files within {}'.format(inDir))
	file_list = getListOfFiles(inDir,'JPG')
	print('Found {} files'.format(len(file_list)))

	print('Extracting geolocation exif data')
	all_metadata = []
	n = 1
	for fn in file_list:
		print('({}/{})'.format(n,len(file_list)), end="\r")
		metadata = get_metadata(fn,et)
		all_metadata.append(metadata)
		n = n+1
	
	print('Exporting EXIF geolocation information')
	df = pd.DataFrame(all_metadata)
	df.to_csv('output.csv')
	
	return None



main()