from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import List

import shutil
import os

from catalog import add_car, search, load_catalog, get_car_by_id, update_car, delete_car, advanced_search

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/images", StaticFiles(directory="images"), name="images")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    catalog = load_catalog()

    return templates.TemplateResponse("index.html",
    {"request":request,"cars":catalog["cars"]})


@app.get("/add", response_class=HTMLResponse)
def add_page(request: Request):

    return templates.TemplateResponse("add.html",{"request":request})


@app.post("/add")
async def add_car_route(
    name: str = Form(...),
    series: str = Form(...),
    code: str = Form(...),
    scale: str = Form(...),
    color: str = Form(...),
    images: List[UploadFile] = File(...)
):
    image_paths = []
    
    # Processar cada imagem enviada
    for image in images:
        path = f"images/{image.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_paths.append(path)

    car = {
        "name": name,
        "series": series,
        "code": code,
        "scale": scale,
        "color": color,
        "images": image_paths
    }

    add_car(car)

    return RedirectResponse(url="/", status_code=303)


@app.get("/edit/{car_id}", response_class=HTMLResponse)
def edit_page(request: Request, car_id: str):
    car = get_car_by_id(car_id)
    if not car:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("edit.html", {"request": request, "car": car})


@app.post("/edit/{car_id}")
async def edit_car_route(
    car_id: str,
    name: str = Form(...),
    series: str = Form(...),
    code: str = Form(...),
    scale: str = Form(""),
    color: str = Form(""),
    images_to_delete: str = Form(""),
    images: List[UploadFile] = File(None)
):
    car = get_car_by_id(car_id)
    if not car:
        return RedirectResponse(url="/", status_code=303)
    
    updated_data = {
        "name": name,
        "series": series,
        "code": code,
        "scale": scale,
        "color": color if color else car.get("color", "")
    }
    
    # Processar imagens atuais e remover as deletadas
    remaining_images = car.get("images", [])
    
    if images_to_delete:
        images_to_delete_list = images_to_delete.split("|")
        remaining_images = [img for img in remaining_images if img not in images_to_delete_list]
        
        # Deletar arquivos do sistema de arquivos
        for img in images_to_delete_list:
            try:
                if os.path.exists(img):
                    os.remove(img)
            except:
                pass
    
    # Se novas imagens foram enviadas, adiciona às existentes
    if images and len(images) > 0 and images[0].filename:
        image_paths = []
        for image in images:
            if image.filename:  # Validar se tem nome
                path = f"images/{image.filename}"
                with open(path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                image_paths.append(path)
        
        if image_paths:
            remaining_images.extend(image_paths)
    
    updated_data["images"] = remaining_images
    update_car(car_id, updated_data)
    return RedirectResponse(url="/", status_code=303)


@app.get("/delete/{car_id}")
def delete_car_route(car_id: str):
    delete_car(car_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str):

    results = search(q)

    return templates.TemplateResponse(
        "search.html",
        {"request":request,"cars":results}
    )


@app.post("/advanced-search", response_class=HTMLResponse)
async def advanced_search_page(
    request: Request,
    name: str = Form(""),
    series: str = Form(""),
    color: str = Form(""),
    code: str = Form("")
):
    criteria = {}
    
    if name:
        criteria["name"] = name
    if series:
        criteria["series"] = series
    if color:
        criteria["color"] = color
    if code:
        criteria["code"] = code
    
    # Se nenhum critério foi preenchido, retorna todos
    if not criteria:
        results = load_catalog()["cars"]
    else:
        results = advanced_search(criteria)
    
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "cars": results}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)