'use client';

import Link from 'next/link';
import { ShoppingBag, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="fixed top-0 w-full z-50 glass-panel border-b border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-20">
                    {/* Logo Area */}
                    <div className="flex-shrink-0 flex items-center gap-4">
                        <Link href="/" className="text-3xl font-black tracking-widest text-white font-tech group">
                            AKIRA<span className="text-red-600 group-hover:neon-text transition-all duration-300">.SYS</span>
                        </Link>

                        {/* System Status Indicator (Desktop) */}
                        <div className="hidden lg:flex items-center gap-2 px-3 py-1 border border-green-900/30 bg-green-900/10 rounded-sm">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                            <span className="text-[10px] font-mono text-green-500 tracking-wider">ONLINE</span>
                        </div>
                    </div>

                    {/* Desktop Menu */}
                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-12">
                            <NavLink href="/">ORIGIN</NavLink>
                            <NavLink href="/catalog">CATALOG</NavLink>
                            <NavLink href="/logistics">LOGISTICS</NavLink>
                        </div>
                    </div>

                    {/* Icons */}
                    <div className="hidden md:flex items-center gap-6">
                        <div className="font-mono text-xs text-gray-500 text-right hidden lg:block">
                            <div>LOC: VOSTOK-1</div>
                            <div>SEC: LEVEL-5</div>
                        </div>
                        <button className="p-2 text-gray-400 hover:text-red-500 transition-colors border border-transparent hover:border-red-500/30 hover:bg-red-500/10 rounded-sm">
                            <ShoppingBag className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="text-gray-400 hover:text-white p-2"
                        >
                            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden bg-black/95 backdrop-blur-xl border-b border-red-900/30"
                    >
                        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                            <MobileNavLink href="/">ORIGIN</MobileNavLink>
                            <MobileNavLink href="/catalog">CATALOG</MobileNavLink>
                            <MobileNavLink href="/logistics">LOGISTICS</MobileNavLink>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
    return (
        <Link
            href={href}
            className="text-gray-400 hover:text-white px-3 py-2 rounded-sm text-sm font-bold tracking-[0.2em] transition-all font-tech glitch-hover border-b-2 border-transparent hover:border-red-500"
        >
            {children}
        </Link>
    );
}

function MobileNavLink({ href, children }: { href: string; children: React.ReactNode }) {
    return (
        <Link
            href={href}
            className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium font-tech"
        >
            {children}
        </Link>
    );
}
