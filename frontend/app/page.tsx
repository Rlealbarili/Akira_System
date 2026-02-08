import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <Navbar />

      {/* Hero Section */}
      <section className="relative flex-grow flex items-center justify-center pt-16 overflow-hidden">
        {/* Background Grid */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black z-10"></div>

        <div className="relative z-20 text-center px-4 max-w-5xl mx-auto space-y-8">
          <div className="inline-block border border-red-500/30 bg-red-500/10 text-red-500 text-xs font-mono px-2 py-1 mb-4 animate-pulse">
            SYSTEM ALERT: NEW INVENTORY DETECTED
          </div>

          <h1 className="text-5xl md:text-8xl font-black tracking-tighter text-white font-tech leading-tight">
            ADVANCED <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-600">TACTICAL</span> <br />
            SOLUTIONS
          </h1>

          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto font-light tracking-wide">
            Engineered for the urban operator. Precision-crafted apparel and equipment for the modern concrete jungle.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
            <button className="px-8 py-4 bg-white text-black font-bold font-tech tracking-wider hover:bg-gray-200 transition-colors w-full sm:w-auto skew-x-[-10deg]">
              <span className="block skew-x-[10deg]">ACCESS CATALOG</span>
            </button>
            <button className="px-8 py-4 border border-white/20 text-white font-bold font-tech tracking-wider hover:bg-white/10 transition-colors w-full sm:w-auto skew-x-[-10deg]">
              <span className="block skew-x-[10deg]">VIEW SPECS</span>
            </button>
          </div>
        </div>
      </section>

      {/* Featured Section Placeholder */}
      <section className="py-24 bg-black border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-tech text-white mb-12 flex items-center gap-4">
            <span className="w-2 h-8 bg-red-600 block"></span>
            FEATURED DEPLOYMENTS
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="aspect-[3/4] bg-white/5 border border-white/10 flex items-center justify-center group hover:border-red-500/50 transition-colors cursor-pointer">
                <span className="font-mono text-gray-600 group-hover:text-red-500">
                  [NO SIGNAL // INDEX {i}]
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
