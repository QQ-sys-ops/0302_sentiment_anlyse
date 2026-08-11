
import   uvicorn

from  engines.contracts.settings import get_settings

if __name__ == '__main__':

    uvicorn.run(app="app.app:app",host=get_settings().HOST,port=get_settings().PORT)


