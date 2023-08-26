import PyPDF2
from receipt_utils import convert_to_float_if_decimal,check_left_to_right
import re
def read_pdf_instacart(file_name):
    # Open the pdf file
    pdf_file = open(file_name, 'rb')

    # Create a pdf reader object
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    # Get the number of pages in the pdf file
    num_pages = pdf_reader.numPages

    all_text=[]
    # Iterate over the pages in the pdf file
    for page_num in range(num_pages):

        # Get the current page
        page = pdf_reader.getPage(page_num)

        # Get the text on the current page
        text = page.extractText()
        all_text= all_text + text.split('\n')
        # Print the text on the current page
        #print(text)

    # Close the pdf file
    pdf_file.close()

    #return all_text

#extracted_list= read_pdf('/home/saeid/Dropbox/a/door.pdf')
#extracted_list= read_pdf('/home/saeid/Dropbox/a/inst.pdf')
    items =[]
    costs =[]
    date_pattern = r'\b\d{1,2}[-/]\d{2}[-/]\d{2}\S*'
    for i, item in enumerate(all_text):
        if 'price' in item:
            costs.append(all_text[i+1])
            items.append(all_text[i-3] + all_text[i-2])
            #print (extracted_list[i-3], extracted_list[i-2], extracted_list[i+1])
        if len(re.findall(date_pattern, item))>0:
            date = re.findall(date_pattern, item)

    print (len(items))
    print (len(costs))
    dates = [date for _ in items]
    path = [file_name for _ in items]
    vendor = ['N/A' for _ in items]
    return items , costs, dates, vendor, path