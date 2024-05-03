from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
@task

def minimal_task():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    download_Order()
    RequestTable = ReadExcell()
    open_robot_order_website()  
    Process_RequestTable(RequestTable)
    archive_receipts()

def screenshot_robot(page,Number): 
   page.locator("#robot-preview-image").screenshot(path = "output/RobotsPhotos/Order{0}imagen.png".format(Number))
   return ("output/RobotsPhotos/Order{0}imagen.png".format(Number))

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot+":align=end"] , target_document= pdf_file,append = True) 
    
def archive_receipts():     
    zip = Archive()
    zip.archive_folder_with_zip("./output/Receipts","./output/OrderPdf.zip")


def CreateDocument(page,Order):
    Content = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(Content,"output/Receipts/ReceiptOrder{}.pdf".format(Order))
    return ("output/Receipts/ReceiptOrder{}.pdf".format(Order))
    

def open_robot_order_website():

   browser.goto("https://robotsparebinindustries.com/#/robot-order")

def CloseModal():
    page = browser.page()
    page.click("text=OK")

def download_Order():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv",overwrite=True)

def ReadExcell():
    table = Tables()
    Contenido =  table.read_table_from_csv("orders.csv",header=True)
    return Contenido


def ProcessRequest(Request):
    """Logica de procesado de un pedido en especifico"""
    CloseModal()  
    page = browser.page()
    page.select_option("#head", Request["Head"])
    page.click("#id-body-"+Request["Body"])
    page.fill("input[placeholder='Enter the part number for the legs']",Request["Legs"])
    page.fill("#address",Request["Address"])
    page.click("text=Preview")
    for i in range (10):
        page.click("#order")
        if page.query_selector("#order-another"):
            screenshot = screenshot_robot(page,Request["Order number"])
            pdf_file=CreateDocument(page,Request["Order number"])
            embed_screenshot_to_receipt(screenshot,pdf_file)
            page.click("#order-another")
            break
    else:
        raise Exception("No se ha podido completar el submit")
    
    
        


    
     

def Process_RequestTable(RequestTable):
    for i in RequestTable:
        ProcessRequest(i)

    

   

