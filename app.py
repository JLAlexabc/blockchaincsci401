from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi import FastAPI, UploadFile, Request, Form,File
from pymongo import MongoClient
from dotenv import dotenv_values
from sampledata import testdata
import blockchain as BC
import crypto as CP
import QRcode as QR

# init classes
app = FastAPI()
templates = Jinja2Templates(directory='templates') # Creating an object for the instance of Jinja - A template engine
blockChain = BC.Blockchain() # Creating an instance of our custom Blockchain
config = dotenv_values(".env") # Configuration for logging into the database (mongodb) for the server.
user_list = []
@app.on_event('startup') # This is to tell the API server to run a function that should be run before the application starts.
async def startup_db_client():
    global user_list
    app.mongodb_client = MongoClient(config['ATLAS_URI']) # Obtain login information for database to login.
    app.database = app.mongodb_client[config['DB_NAME']] # Obtaining name of the database.
    # print(app.mongodb_client.list_database_names()) # prints the database names available from the mongodb client.
    print("Connected to the MongoDB database!") # lets us know that we've connected to the database successfully.
    user_list = list(app.database['users'].find({},{'_id':False}))

    # test for block chain
    new_product = {
        "product_name": "p1",
        "product_ID": "665",
        "ID_cert":"asdasdasd",
        "msg":"dsadsadas",
        "code_64":"sdasdsadasd",
        "x_index": len(blockChain.chain)
    }
    await mine_block_x(new_product)
    await mine_block_x(new_product)
    await mine_block_x(new_product)

    new_transcation = {
        "product_ID": "asdawww",
        "Seller_ID": "4",
        "Buyer_ID": "5",
        "x_index": 999,
    }
    await mine_block_y(data=new_transcation,x_index=1)
    await mine_block_y(data=new_transcation,x_index=1)
    await mine_block_y(data=new_transcation,x_index=1)

    await mine_block_y(data=new_transcation,x_index=2)
    await mine_block_y(data=new_transcation,x_index=2)

    await mine_block_y(data=new_transcation,x_index=3)
    await mine_block_y(data=new_transcation,x_index=3)
    await mine_block_y(data=new_transcation,x_index=3)
    await mine_block_y(data=new_transcation,x_index=3)

@app.on_event("shutdown") # This is to tell the API server to run a function that should be run when the application is shutting down.
def shutdown_db_client(): # this is the function that will end the connection with the server and database.
    app.mongodb_client.close()

@app.get("/db/getusers",response_description="List all Users") # this is used to obtain all the users from the database. async is the fine to ensure that nothing else runs until this process is done.
async def get_users():
    ''' get all users from database'''
    global user_list
    user_list =list(app.database['users'].find({},{'_id':False}))
    return user_list

@app.get("/db/inser_test_data")
async def insert_data():
    ''' insert test to database'''
    app.database['users'].insert_many(testdata)
    return "test users inserted"

# index page
@app.get('/',response_class=HTMLResponse) # Tells function to response with a html page as its main page. This can be shown based on having a '/' only.
async def index(request:Request):
    return templates.TemplateResponse('index.html',context={"request":request}) # since we are using a template library to manage our website (i.e., Jinja2), we are returning the name of the HTML file we want to return and

# about page
@app.get('/about',response_class=HTMLResponse) # Tells function to response with a about page when a user clicks on the link on the website. This can be shown based on having a '/about' only.  
async def about(request:Request):
    about_infor = {
        "msg":"Hello there"
    }
    return templates.TemplateResponse('about.html',context={"request":request,"data":about_infor}) # since we are using a template library (i.e., Jinja2), we need to indicate which file we want to return along with creating variables for the request, and data for whatever information we want to put on the website from the about_infor variable.

# for view blockchain page 
@app.get("/viewblockchain",response_class=HTMLResponse)
async def get_blockChain_infor(request:Request):
    if not blockChain.is_chain_valid():
        return FastAPI.HTTPException(
            status_code=400, detail="The block chain is invalid"
        )
    data = {
        "theChainX" : blockChain.chain,
        "theChainY" : blockChain.chain2
        }    
    return templates.TemplateResponse('blockchain.html',context={"request":request,"data":data})

# get all users inforamton page 
@app.get("/u/allusers",response_class=HTMLResponse)
async def get_users_page(request:Request):
    global user_list
    data = {"user_list" : user_list}
    return templates.TemplateResponse('showusers.html',context={"request":request,"data":data})

# get keys
@app.get("/u/getkeys/{userid}/{publickey}")
async def get_keys(userid,publickey):
    global user_list
    filename = publickey+'.der'
    key_str = user_list[int(userid)][publickey]
    key = CP.load_keys(key_str)
    with open(filename,'wb') as infile:
        infile.write(key.export_key(format="DER"))

    headers = {'Content-Disposition': f'inline; filename="{filename}"'}
    return FileResponse(filename, headers=headers, media_type='application/text') 

# upload key file
@app.post("/u/uploadkey/") # when a user wants to upload a file onto the server, the server looks for this URL within the post function and runs the function below it 
async def create_upload_file(file: UploadFile): # this function obtain a file from a user. It uses the reserve await to wait for the file to be fully read for it to then be passed along to the upload_key variable              
    upload_key = await file.read()
    # print(upload_key)
    CP.load_keys(upload_key)
    return {"filename": file.filename}
# create a prouduct ID
@app.get("/u/getProductID") # when obtaining a product ID, dis will run the function below it.
async def get_productID(private_key='fake key here'):  # This gets the product ID by obtaining the private key from the file and then returns the data to create the QR code. 
    # print(private_key)
    return QR.create_productID(key=private_key)

@app.get("/u/getproductQRcode",response_class=HTMLResponse) # This is used to get the QR code.
async def get_QRcode(request:Request,productID='546874452',):
    '''return a base64 str image data Example: <img src="data:image/png;base64,{}">'''
    QRcode = {
        'imgdata': str(QR.create_QRcode(productID))
    }
    # print(QR.create_QRcode(productID))
    return templates.TemplateResponse('QRcode.html',context={"request":request,'QRcode':QRcode})

# get user products' Information (all)
@app.get("/u/viewproduct/{userid}",response_class=HTMLResponse) # this is used to request the QR code to be shown on the website. The function that makes this process happen is below:
async def view_user_products(userid,request:Request):
    # print(user_list[int(userid)]['products'])
    data = {
        'products':user_list[int(userid)]['products'],
        'user_name':user_list[int(userid)]['user_name'],
        'index':userid
        }
    return templates.TemplateResponse('viewproduct.html',context={"request":request,'data':data})

# get user products' Information (detail)
@app.get("/u/viewproduct/productdetail/{userid}/{productid}",response_class=HTMLResponse) # this is used to request the QR code to be shown on the website. The function that makes this process happen is below:
async def view_product_detail(userid,productid,request:Request):
    data = {
        'owner': user_list[int(userid)],
        'product': (p for p in user_list[int(userid)]['products'] if p['product_ID']==productid),
        'transactions':user_list[int(userid)]['transactions'][0]
        }
    return templates.TemplateResponse('productdetail.html',context={"request":request,'data':data})

# add product html page
@app.get("/u/addproductpage/{userid}",response_class=HTMLResponse) 
async def add_product_page(userid,request:Request):
    data = {
        'index':userid,
        'user_name':user_list[int(userid)]['user_name'],
    }
    return templates.TemplateResponse('addproduct.html',context={"request":request,'data':data})

# handle add product request rout
@app.post("/u/addproduct/{userid}") 
async def add_product(userid,request:Request,username:str=Form(...),productname:str=Form(...),exinfor:str=Form()):
    # get private key and create productID and certificate for the productID, also QRcode
    key_str = user_list[int(userid)]["user_private_key"]
    key = CP.load_keys(key_str)
    productId,certif,msg = QR.create_productID(key=key,productInfo=exinfor)
    # print(productId,certif,msg)
    qrcode = QR.create_QRcode(productId,userid)
    # save new product into DB and block chain
    new_product = {
        "product_name": productname,
        "product_ID": productId,
        "ID_cert":certif,
        "msg":msg,
        "code_64":qrcode,
        "x_index": len(blockChain.chain)
    }
    productlist = user_list[int(userid)]["products"]
    productlist.append(new_product)

    # save into db
    filter = {'index':int(userid)}
    newvalues = {'$set':{'products':productlist}}
    app.database['users'].update_one(filter,newvalues)  # should be in try catch

    # update local user_list
    await get_users()

    #save new product into blockchain minX
    await mine_block_x(data=new_product)

    #redirect to view user's products page 
    return await view_user_products(userid=userid,request = request)

# transcation html page only verify owner-ship cerificate vaild
@app.get("/transcation/{userid}/{pid}",response_class=HTMLResponse) 
async def transcation(userid,pid,request:Request):
    owner = user_list[int(userid)]
    product = [p for p in user_list[int(userid)]['products'] if p['product_ID']==pid]
    
    pub_key_str = owner["user_public_key"]
    certificate = bytearray.fromhex(product[0]["ID_cert"])
    msg = bytes(product[0]["msg"],encoding='utf-8')
    pub_key_obj = CP.load_keys(pub_key_str)  # bytes(content_str,encoding='utf-8')
    cert_result = CP.verify(key=pub_key_obj,signature=certificate,msg=msg)
    chain_result = blockChain.is_chain_valid()
    data = {
        'owner': owner,
        'product': product[0],
        'cert_result':cert_result,   
        'chain_result':chain_result
    }
    return templates.TemplateResponse('transcation.html',context={"request":request,'data':data})


# handle place order request
@app.post("/transcation/placeorder/{sellerid}/{pid}/") 
async def transcation_submit(request:Request,sellerid,pid,filep:UploadFile=File(...)):
    # get key upload if any
    upload_key = await filep.read()
    try:
        key = CP.load_keys(upload_key)
    except:
        return "Invailed Key File."
    # find buyer id by using the key upload
    buyerid = [b for b in user_list if b['user_private_key'] == key.export_key(format='DER').hex()][0]['index']
    x_index = [xi['x_index'] for xi in user_list[int(sellerid)]["products"] if xi['product_ID'] == pid][0]

    new_transcation = {
        "product_ID": pid,
        "Seller_ID": sellerid,
        "Buyer_ID": buyerid,
        "x_index": x_index,
    }
    # print(new_transcation)
    # now create a new Y block for this transcation, change owner ship of the product
    await mine_block_y(data=new_transcation,x_index=x_index)

    # when onwer ship changed 
    # 1. remove product from pre_onwer --- delete the product record from it(database)
    filter = {'index':int(sellerid)}
    updated_seller_product_list = [p for p in user_list[int(sellerid)]['products'] if p['product_ID']!=pid]
    newvalues = {'$set':{'products':updated_seller_product_list}}
    app.database['users'].update_one(filter,newvalues)  # should be in try catch

    # 2. add new product from new owner --- add record to database
    the_product = [p for p in user_list[int(sellerid)]['products'] if p['product_ID']==pid][0]   # get the product
    certif,msg = QR.re_ceritifcate(product_id=the_product["product_ID"],key=key,productInfo=the_product['msg'])
    qrcode = QR.create_QRcode(the_product["product_ID"],buyerid)
    new_product = {
        "product_name": the_product["product_name"],
        "product_ID": the_product["product_ID"],
        "ID_cert":certif,
        "msg":msg,
        "code_64":qrcode,
        "x_index": the_product["x_index"]
    }
    # print(new_product)
    filter = {'index':buyerid}
    updated_buyer_product_list = user_list[int(buyerid)]['products'] 
    updated_buyer_product_list.append(new_product)
    newvalues = {'$set':{'products':updated_buyer_product_list}}
    app.database['users'].update_one(filter,newvalues)  # should be in try catch
    # 3. update user_list in local
    await get_users()
    # return to this product detail informaiton page and show transaction is changed
    return await view_user_products(userid=buyerid,request=request)


# get the chain
@app.get("/blockchain")
async def get_blockChain():
    if not blockChain.is_chain_valid():
        return FastAPI.HTTPException(
            status_code=400, detail="The block chain is invalid"
        )
        
    return blockChain.chain

# @app.post("/x/mineblock/")
async def mine_block_x(data:str):
    if not blockChain.is_chain_valid():
        return FastAPI.HTTPException(
            status_code=400, detail="The block chain is invalid"
        )
        
    block = blockChain.minex(data=data)
    # print(blockChain.displayx())
    return block

@app.get("/x/viewchain/")
async def view_x():
    if not blockChain.is_chain_valid():
        return FastAPI.HTTPException(
            status_code=400, detail="The block chain is invalid"
        )
    theChain = blockChain.displayx()

    return theChain

# @app.post("/y/mineblock/")
async def mine_block_y(data:str, x_index:int):
    if not blockChain.is_chain_valid():
        return FastAPI.HTTPException(
            status_code=400, detail="The block chain is invalid"
        )
    block = blockChain.miney(data=data,x_index=x_index)

    return block

@app.get("/y/viewchain/")
async def view_y():
    if not blockChain.is_chain_valid():
        return FastAPI.HTTPException(
            status_code=400, detail="The block chain is invalid"
        )
    theChain = blockChain.displayy()

    return theChain
