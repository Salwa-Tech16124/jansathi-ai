import React from 'react';
import { useLocation } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Footer } from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  return (
    <div className="flex flex-col min-h-screen bg-gov-ash">
      <Navbar />
      <main key={location.pathname} className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 page-fade-in">
        {children}
      </main>
      <Footer />
    </div>
  );
};
