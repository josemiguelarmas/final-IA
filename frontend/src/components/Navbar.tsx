import React from 'react';
import { Scale, RotateCcw, Plus } from 'lucide-react';

interface NavbarProps {
  onOpenImport: () => void;
  onResetSamples: () => void;
  isLoading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenImport, onResetSamples, isLoading }) => {
  return (
    <header className="shrink-0 bg-navy text-white">
      <div className="flex h-14 items-center justify-between gap-4 px-4 lg:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <Scale className="h-5 w-5 shrink-0 text-icesi-amber" aria-hidden="true" />
          <div className="min-w-0 leading-tight">
            <h1 className="truncate font-serif text-lg font-semibold tracking-tight">Consultorio Jurídico</h1>
            <p className="truncate text-xs text-white/70">
              Universidad Icesi · Supervisión de notificaciones de Mantis
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={onResetSamples}
            disabled={isLoading}
            className="btn border border-white/25 text-white/90 hover:bg-white/10 hover:text-white"
          >
            <RotateCcw className={`h-4 w-4 ${isLoading ? 'animate-spin motion-reduce:animate-none' : ''}`} aria-hidden="true" />
            <span className="hidden md:inline">Restaurar casos de muestra</span>
            <span className="sr-only md:hidden">Restaurar casos de muestra</span>
          </button>

          <button
            type="button"
            onClick={onOpenImport}
            className="btn bg-icesi-amber font-semibold text-navy hover:bg-[#ffc84a]"
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">Importar notificación</span>
            <span className="sm:hidden">Importar</span>
          </button>
        </div>
      </div>
    </header>
  );
};
