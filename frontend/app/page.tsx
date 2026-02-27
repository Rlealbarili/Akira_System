import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { client } from '@/lib/shopify';
import Image from 'next/image';
import Link from 'next/link';

// Force dynamic rendering to ensure fresh data
export const dynamic = 'force-dynamic';

type ProductCard = {
  id: string;
  handle: string;
  title: string;
  images: Array<{
    src: string;
    altText?: string | null;
  }>;
  variants: Array<{
    price: {
      amount: string;
      currencyCode: string;
    };
  }>;
};

export default async function Home() {
  // Fetch products from Shopify
  const products = (await client.product.fetchAll()) as ProductCard[];

  return (
    <main className="min-h-screen flex flex-col">
      <Navbar />

      {/* Hero Section */}
      <section className="relative flex-grow flex items-center justify-center pt-16 overflow-hidden min-h-[80vh]">
        {/* Background Grid */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black z-10"></div>

        <div className="relative z-20 text-center px-4 max-w-5xl mx-auto space-y-8">
          <div className="inline-block border border-red-500/30 bg-red-500/10 text-red-500 text-xs font-mono px-2 py-1 mb-4 animate-pulse">
            SYSTEM ALERT: NEW INVENTORY DETECTED
          </div>

          <h1 className="text-5xl md:text-8xl font-black tracking-tighter text-white font-tech leading-tight">
            PREMIUM <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-600">SETUP</span> <br />
            HARDWARE
          </h1>

          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto font-light tracking-wide">
            Curated keycaps, mechanical keyboards, and accessories for enthusiasts who take their setup seriously.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
            <Link href="/catalog" className="px-8 py-4 bg-white text-black font-bold font-tech tracking-wider hover:bg-gray-200 transition-colors w-full sm:w-auto skew-x-[-10deg]">
              <span className="block skew-x-[10deg]">ACCESS CATALOG</span>
            </Link>
            <button className="px-8 py-4 border border-white/20 text-white font-bold font-tech tracking-wider hover:bg-white/10 transition-colors w-full sm:w-auto skew-x-[-10deg]">
              <span className="block skew-x-[10deg]">VIEW SPECS</span>
            </button>
          </div>
        </div>
      </section>

      {/* Featured Section */}
      <section className="py-24 bg-black border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-tech text-white mb-12 flex items-center gap-4">
            <span className="w-2 h-8 bg-red-600 block"></span>
            FEATURED DEPLOYMENTS
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {products.slice(0, 3).map((product) => (
              <Link href={`/product/${product.handle}`} key={product.id} className="group block">
                <div className="aspect-[3/4] bg-white/5 border border-white/10 relative overflow-hidden transition-all duration-300 group-hover:border-red-500/50">
                  {product.images[0] && (
                    <Image
                      src={product.images[0].src}
                      alt={product.images[0].altText || product.title}
                      fill
                      className="object-cover opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-500"
                    />
                  )}

                  {/* Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                    <span className="text-red-500 font-mono text-xs mb-2">
                      ID: {product.id.substring(product.id.lastIndexOf('/') + 1)}
                    </span>
                  </div>
                </div>

                <div className="mt-4 space-y-1">
                  <h3 className="text-lg font-bold text-white font-tech group-hover:text-red-500 transition-colors truncate">
                    {product.title}
                  </h3>
                  <p className="text-gray-400 font-mono text-sm">
                    {product.variants[0]?.price.amount} {product.variants[0]?.price.currencyCode}
                  </p>
                </div>
              </Link>
            ))}

            {products.length === 0 && (
              <div className="col-span-3 text-center text-gray-500 font-mono py-12 border border-dashed border-white/10">
                ⚠️ NO SIGNAL DETECTED FROM INVENTORY SYSTEM
              </div>
            )}
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
