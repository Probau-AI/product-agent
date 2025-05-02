from app.models import Product, Dimensions

floors = [
    Product(
        name="Laminat 8.0 Petterson Eiche Natur",
        price_eur=12.95,
        product_url="https://www.hornbach.de/p/laminat-8-0-petterson-eiche-natur/6087617/",
        dimensions=Dimensions(
            height=0.8,
            width=24.4,
            depth=138.0
        ),
        material="wood",
        brand="Kronotex",
        rating=4.7,
        category="floors",
        image_url="https://media.hornbach.de/hb/packshot/as.46413810.jpg?dvid=8",
    ),
    Product(
        name="SKANDOR Laminat 8.0 Ahmara Oak",
        image_url="https://media.hornbach.de/hb/packshot/as.47351907.jpg?dvid=8",
        price_eur=10.95,
        product_url="https://www.hornbach.de/p/skandor-laminat-8-0-ahmara-oak/10132552/",
        dimensions=Dimensions(height=0.8, width=19.3, depth=138.3),
        weight=12.63,
        color="Oak",
        material="HDF Quellungsarm (Trägerplatte), Wood",
        category="Laminate",
        brand="SKANDOR",
        rating=4.2,
        delivery_time="Approximately 5 working days",
        description="This laminate flooring has a rustic, old wood effect and is suitable for various indoor applications. It's designed for both private and commercial use, easy to install, and compatible with underfloor heating.",
    ),
    Product(
        name="SKANDOR Laminat 7+2 Easily Ash",
        image_url="https://media.hornbach.de/hb/packshot/as.46853066.jpg?dvid=8",  # Add image URL if available
        price_eur=9.95,  # per m2
        product_url="https://www.hornbach.de/p/skandor-laminat-72-easily-ash/6395253/",
        dimensions=Dimensions(height=0.9, width=19.3, depth=138.3),
        weight=14.54,  # per pack
        color="Esche (Light Ash)",
        material="HDF (High-Density Fiberboard), Wood",
        category="Bodenbeläge & Fliesen Laminat",
        brand="SKANDOR",
        rating=3.0,
        delivery_time="Approximately 5 working days",  # Or 1-2 for samples
        description="Helles Laminat in Holzoptik ist nach wie vor ein Renner. Nehmen Sie nur das Easily Ash von SKANDOR als Beispiel. Es kommt mit der Oberflächenstruktur Authen.",
    ),
    Product(
        name="SKANDOR Laminat Midday Oak Landhausdiele 1380 x 244 x 8 mm",
        image_url="https://media.hornbach.de/hb/packshot/as.46056854.jpg?dvid=8",
        price_eur=10.95,
        product_url="https://www.hornbach.de/p/skandor-laminat-midday-oak-landhausdiele-1380-x-244-x-8-mm/5901385/",
        dimensions=Dimensions(height=0.8, width=24.4, depth=138.0),
        weight=None, # Weight is not available
        color="Midday Oak",
        material="HDF, Hartholz, Massivholz, Stahl",
        category="Bodenbeläge & Fliesen",
        brand="SKANDOR",
        rating=3.8,
        delivery_time="Approximately 5 working days",
        description="This laminate flooring has an echtholzoptik (real wood look) surface and is suitable for various indoor spaces. It is classified for medium traffic areas.  Customers have praised its appearance, ease of installation, and durability.",
    ),
    Product(
        name="SKANDOR Laminat 7.2 Easily Ash",
        image_url="https://media.hornbach.de/hb/packshot/as.46853066.jpg?dvid=8",
        price_eur=9.95,
        product_url="https://www.hornbach.de/p/skandor-laminat-72-easily-ash/6395253/",
        dimensions=Dimensions(height=0.9, width=19.3, depth=138.3),
        weight=None,
        color="Easily Ash",
        material="HDF",
        category="Laminate",
        brand="SKANDOR",
        rating=4.5,
        delivery_time="Approximately 5 working days",
        description="The SKANDOR 7.2 Easily Ash laminate flooring combines a beautiful, light, natural look with high durability and easy installation.  It's suitable for various living spaces and commercial areas with moderate use.",
    )

]
