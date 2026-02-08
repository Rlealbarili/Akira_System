'use client';

import Link from 'next/link';
import { ShoppingBag, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="fixed top-0 w-full z-50 bg-black/80 backdrop-blur-md border-b border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <div className="flex-shrink-0">
                        <Link href="/" className="text-2xl font-bold tracking-widest text-white font-tech hover:text-red-500 transition-colors">
                            AKIRA<span className="text-red-600">.SYS</span>
                        </Link>
                    </div>

                    {/* Desktop Menu */}
                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-8">
                            <NavLink href="/">ORIGIN</NavLink>
                            <NavLink href="/catalog">GEAR</NavLink>
                            <NavLink href="/logistics">LOGISTICS</NavLink>
                        </div>
                    </div>

                    {/* Icons */}
                    <div className="hidden md:flex items-center gap-4">
                        <button className="p-2 text-gray-400 hover:text-white transition-colors">
                            <ShoppingBag className="w-6 h-6" />
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
                        className="md:hidden bg-black border-b border-white/10"
                    >
                        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                            <MobileNavLink href="/">ORIGIN</MobileNavLink>
                            <MobileNavLink href="/catalog">GEAR</MobileNavLink>
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
            className="text-gray-300 hover:text-red-500 px-3 py-2 rounded-md text-sm font-medium tracking-widest transition-colors font-tech"
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
