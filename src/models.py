from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase

class AbstractModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

class ProductModel(AbstractModel):
    __tablename__ = "products"
    ms_code: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    retail_price: Mapped[float] = mapped_column()
    mt10: Mapped[float] = mapped_column()
    image: Mapped[str] = mapped_column()
    nicotine_strength: Mapped[float] = mapped_column()
    taste: Mapped[str] = mapped_column()
    snus_type: Mapped[str] = mapped_column() 
    brand: Mapped[str] = mapped_column()
    currency: Mapped[str] = mapped_column()
    sale_price: Mapped[float] = mapped_column()
    is_sale: Mapped[bool] = mapped_column()
    is_popular: Mapped[bool] = mapped_column(default=False)
    search_name: Mapped[str] = mapped_column()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "mt10": self.mt10 if not self.sale_price else self.sale_price,
            "retail_price": self.retail_price if not self.sale_price else self.sale_price
        }
        
if __name__ == "__main__":
    ...