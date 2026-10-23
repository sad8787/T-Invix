import type { Product, ProductsResponse } from "../lib/types";

export const dynamic = "force-dynamic";

async function getProducts(): Promise<Product[]> {
    const api = process.env.INTERNAL_API_URL ?? "http://backend:8000";

    try {
        const response = await fetch(`${api}/api/v1/products`, {
            cache: "no-store",
        });

        if (!response.ok) return [];

        const data = (await response.json()) as ProductsResponse;
        return data.items;
    } catch {
        return [];
    }
}

export default async function CatalogPage() {
    const products = await getProducts();
    const mediaBase = process.env.NEXT_PUBLIC_MEDIA_BASE_URL ?? "/media";

    return (
        <main className="page">
            <header className="header">
                <h1>Каталог</h1>
                <p>Список товаров</p>
            </header>

            {products.length === 0 ? (
                <p className="empty">Пока товаров нет.</p>
            ) : (
                <ul className="products">
                    {products.map((product) => (
                        <li className="product" key={product.id}>
                            <img
                                className="product-image"
                                src={`${mediaBase}/${product.image_key
                                    .split("/")
                                    .map(encodeURIComponent)
                                    .join("/")}`}
                                alt={product.name}
                                loading="lazy"
                            />
                            <div className="product-info">
                                <h2>{product.name}</h2>
                                <time dateTime={product.created_at}>
                                    {new Date(product.created_at).toLocaleDateString("ru-RU")}
                                </time>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
        </main>
    );
}
