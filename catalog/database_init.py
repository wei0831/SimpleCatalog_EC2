# Date: 11/13/2015
# Author: Jack Chang (wei0831@gmail.com)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db = sessionmaker(bind=engine)()

# Clear All Tables
for table in reversed(Base.metadata.sorted_tables):
    db.execute(table.delete())
db.commit()

# Dummy Category
db.add(Category(name="Soccer"))
db.commit()
db.add(Category(name="Basketball"))
db.commit()
db.add(Category(name="Baseball"))
db.commit()
db.add(Category(name="Frisbee"))
db.commit()
db.add(Category(name="Snowboarding"))
db.commit()
db.add(Category(name="Rock Climbing"))
db.commit()

# Dummy Item
db.add(Item(title="Shinguards",
            description="Shinguards description", category_id=1, user_id=0))
db.commit()
db.add(Item(title="Goggles",
            description="Goggles description", category_id=5, user_id=0))
db.commit()
db.add(Item(title="Snowboarding",
            description="Best for any terrain and conditions All-mountain \
                        Snowboards perform anywhere on a mountian.",
            category_id=5, user_id=0))
db.commit()
