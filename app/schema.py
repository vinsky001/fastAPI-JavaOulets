from pydantic import BaseModel
from typing import List, Optional

class JavaOutlet(BaseModel):
    id: int
    name: str
    location: str
    rating: Optional[float] = None
    is_open: bool
    
class JavaOutletList(BaseModel):
    outlets: List[JavaOutlet]
    
class JavaOutletCreate(BaseModel):
    name: str
    location: str
    rating: Optional[float] = None
    is_open: bool
    
class JavaOutletProduct(BaseModel):
    id: int
    outlet_id: int
    product_name: str
    price: float
    is_available: bool            
    
class JavaOutletWithProducts(BaseModel):
    outlet: JavaOutlet
    products: List[JavaOutletProduct]
    
class JavaOutletProductCreate(BaseModel):
    outlet_id: int
    product_name: str
    price: float
    is_available: bool
    
#Order related schemas
class JavaOutletOrder(BaseModel):
    id: int
    outlet_id: int
    product_ids: List[int]
    total_price: float
    is_completed: bool        