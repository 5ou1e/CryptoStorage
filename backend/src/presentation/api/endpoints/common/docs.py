from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get(
    "/rapidoc",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def get_rapidoc():
    html_content = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>RapiDoc</title>
                <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
            </head>
            <body>
                <rapi-doc spec-url="/api/openapi.json"></rapi-doc>
            </body>
        </html>
    """
    return HTMLResponse(content=html_content)


@router.get(
    "/elements",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def get_elements_docs():
    html_content = """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>Elements in HTML</title>
            <!-- Embed elements Elements via Web Component -->
            <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
            <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
          </head>
          <body>
        
            <elements-api
              apiDescriptionUrl="/api/openapi.json"
              router="hash"
              layout="sidebar"
            />
        
          </body>
        </html>
    """
    return HTMLResponse(content=html_content)
