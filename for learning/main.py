from fastapi import FastAPI, Request
from mockData import products
from dtos import ProductDTO

app = FastAPI()

@app.get("/")
def home():
  return "Welcome to Spider Society!"

@app.get("/contact")
def contact():
  return "Let's connect."

@app.get("/products")
def getProducts():
  return products

# Path Params
@app.get("/product/{product_id}")
def getProductById(product_id: int):
  for i in products:
    if(i.get("id") == product_id):
      return i
    
  return { "error": "Product not Found for this ID."}

# Query Params
@app.get("/products/search")
def searchProduct(title:str):
  for i in products:
    if(i.get("title") == title):
      return i
  
  return { "error": f"Product not Found with title {title}"}

# Dynamic number of query params
@app.get("/random")
def randomQueryParam(request: Request):
  params = dict(request.query_params)

  return {
    "searchValue"  : params.get("search"),
    "count": params.get("count")
  }


# HTTP POST method
@app.post("/product/add")
def createProduct(data: ProductDTO):
  productData = data.model_dump() #converts a data model instance into a standard Python dictionary
  products.append(productData)

  return {
    "status": "200",
    "message": "Product created successfully",
    "data": products
  }

# HTTP PUT method
@app.put("/product/update/{product_id}")
def updateProduct(product_id: int, data: ProductDTO):

# Enumerate allows you to loop through an iterable (like a list, tuple, or string) while keeping track of both the index and the value of each item. It returns an enumerate object that yields pairs in the form of (index, item)
  for i, prod in enumerate(products): 
    if(prod.get("id") == product_id):
      products[i] = data.model_dump()
      return {
        "status": "200",
        "message": "Product updated successfully",
        "data": prod
      }

  return {
    "status": "failed",
    "message": f"Product not found with ID {product_id}",
  }


#  HTTP DELETE method
@app.delete("/product/delete/{product_id}")
def deleteProduct(product_id: int):
  for i, prod in enumerate(products):
    if(prod.get("id") == product_id):
      removed_product = products.pop(i)
      return {
        "status": "200",
        "message": "Product deleted successfully",
        "data": removed_product
      }
  
  return {
    "status": "failed",
    "message": f"Product with ID {product_id} not found.",
  }
    

