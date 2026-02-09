from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, condecimal, conint, constr, ConfigDict

CurrencyCode = constr(min_length=3, max_length=3)
PhoneNumber = constr(min_length=7, max_length=20)


class JavaOutlet(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: int
    name: str
    location: str
    city: str              
    county: str            
    street_address: Optional[str]  
    phone_number: Optional[str]    
    is_open: bool          
    opening_time: Optional[str]    
    closing_time: Optional[str]
    rating: Optional[float]
    last_inspected_at: Optional[datetime]
    
class JavaOutletList(BaseModel):
    outlets: List[JavaOutlet]
    
class JavaOutletCreate(BaseModel):
    name: str
    location: str
    city: str
    county: str
    street_address: str | None = None
    phone_number: str | None = None
    rating: float | None = None
    is_open: int
    opening_time: str | None = None
    closing_time: str | None = None
    
class JavaOutletMenuItem(BaseModel):
    id: int
    outlet_id: int
    menu_item_name: constr(min_length=2, max_length=120)
    category: Optional[constr(min_length=2, max_length=80)] = None
    sku: Optional[constr(min_length=2, max_length=40)] = None
    price: condecimal(max_digits=8, decimal_places=2)
    currency: CurrencyCode = Field(default="KES", description="ISO-4217 currency code")
    is_available: bool
    has_dairy: bool = False
    is_seasonal: bool = False


class JavaOutletProduct(JavaOutletMenuItem):
    """Backward-compatible alias for menu items per outlet branch."""
    pass
    
class JavaOutletWithMenu(BaseModel):
    outlet: JavaOutlet
    menu_items: List[JavaOutletMenuItem]


class JavaOutletWithProducts(BaseModel):
    """Backward-compatible response for outlet menu items."""
    outlet: JavaOutlet
    products: List[JavaOutletProduct]
    
class JavaOutletMenuItemCreate(BaseModel):
    outlet_id: int
    menu_item_name: constr(min_length=2, max_length=120)
    category: Optional[constr(min_length=2, max_length=80)] = None
    sku: Optional[constr(min_length=2, max_length=40)] = None
    price: condecimal(max_digits=8, decimal_places=2)
    currency: CurrencyCode = Field(default="KES", description="ISO-4217 currency code")
    is_available: bool
    has_dairy: bool = False
    is_seasonal: bool = False


class JavaOutletProductCreate(JavaOutletMenuItemCreate):
    """Backward-compatible alias for menu item creation per outlet branch."""
    pass
    
#Order related schemas
class JavaOutletOrder(BaseModel):
    id: int
    outlet_id: int
    product_ids: List[int]
    total_price: condecimal(max_digits=10, decimal_places=2)
    currency: CurrencyCode = Field(default="KES", description="ISO-4217 currency code")
    is_completed: bool
    status: constr(min_length=3, max_length=32) = "pending"
    placed_at: datetime
    completed_at: Optional[datetime] = None
    payment_method: Optional[constr(min_length=3, max_length=40)] = None
    notes: Optional[constr(max_length=280)] = None


class JavaOutletOrderCreate(BaseModel):
    outlet_id: int
    product_ids: List[int]
    payment_method: Optional[constr(min_length=3, max_length=40)] = None
    notes: Optional[constr(max_length=280)] = None


class JavaOutletOrderSummary(BaseModel):
    outlet_id: int
    outlet_name: str
    total_orders: conint(ge=0)
    total_revenue: condecimal(max_digits=12, decimal_places=2)
    currency: CurrencyCode = "KES"
