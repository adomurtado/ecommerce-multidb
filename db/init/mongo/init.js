db = db.getSiblingDB('ecom');
db.createCollection('produk_metadata');
db.produk_metadata.insertMany([
  {
    "sku": "P123",
    "deskripsi": "Laptop gaming dengan pendingin cair"
  }
]);