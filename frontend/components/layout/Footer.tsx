export default function Footer() {
    return (
        <footer className="bg-black border-t border-white/10 py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-sm text-gray-400">

                    {/* Brand */}
                    <div className="space-y-4">
                        <h3 className="text-white font-tech tracking-widest">AKIRA SYSTEMS INC.</h3>
                        <p>Advanced tactical solutions for the modern urban environment.</p>
                        <div className="flex items-center gap-2 text-xs font-mono text-green-500">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            SYSTEM STATUS: ONLINE
                        </div>
                    </div>

                    {/* Links */}
                    <div className="space-y-4">
                        <h3 className="text-white font-tech tracking-widest">PROTOCOLS</h3>
                        <ul className="space-y-2">
                            <li><a href="#" className="hover:text-red-500 transition-colors">Shipping Policy</a></li>
                            <li><a href="#" className="hover:text-red-500 transition-colors">Return Auth (RMA)</a></li>
                            <li><a href="#" className="hover:text-red-500 transition-colors">System Specs</a></li>
                        </ul>
                    </div>

                    {/* Newsletter */}
                    <div className="space-y-4">
                        <h3 className="text-white font-tech tracking-widest">DATA LINK</h3>
                        <p>Subscribe for equipment drops and system updates.</p>
                        <div className="flex">
                            <input
                                type="email"
                                placeholder="ENTER EMAIL"
                                className="bg-white/5 border border-white/10 px-4 py-2 text-white focus:outline-none focus:border-red-500 w-full"
                            />
                            <button className="bg-red-600 text-white px-4 py-2 font-tech hover:bg-red-700 transition-colors">
                                INIT
                            </button>
                        </div>
                    </div>

                </div>

                <div className="mt-12 pt-8 border-t border-white/10 text-center text-xs font-mono text-gray-600">
                    &copy; 2026 AKIRA SYSTEMS. ALL RIGHTS RESERVED. // VOSTOK SERVER
                </div>
            </div>
        </footer>
    );
}
