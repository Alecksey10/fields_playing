from typing import Optional
from pydantic import BaseModel


# путь закачки (только один путь)
# Какая область (только одна область за раз)
# По какой теме отчёт (только одна тема за раз)
# какой год
# какой тип документа

class DownloadScheme(BaseModel):
    download_path:str
    city:str
    theme:str
    year:str
    year_from:str
    year_to:str
    document_type:str

class DownloadResult(BaseModel):
    success:bool
    path:Optional[str]


if __name__=="__main__":
    ds = DownloadScheme(download_path='./test', 
                        city="Москв",
                        theme="test",
                        year="test2",
                        year_from="test2",
                        year_to="test2",
                        document_type="CSV")
    print(ds)