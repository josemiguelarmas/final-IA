import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardStats } from './components/DashboardStats';
import { NotificationList } from './components/NotificationList';
import { NotificationDetail } from './components/NotificationDetail';
import { ImportModal } from './components/ImportModal';
import { ConfirmDialog } from './components/ConfirmDialog';
import { Toast, ToastState } from './components/Toast';
import { NotificationItem, DashboardStatsData, HumanDecision } from './types';
import { fetchNotifications, fetchStats, submitHumanReviewBatch, resetSamples } from './api';
import { groupThreads } from './lib/threads';

export const App: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [stats, setStats] = useState<DashboardStatsData | null>(null);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('todas');
  const [statusFilter, setStatusFilter] = useState<string>('todos');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isImportModalOpen, setIsImportModalOpen] = useState<boolean>(false);
  const [isResetConfirmOpen, setIsResetConfirmOpen] = useState<boolean>(false);
  // En pantallas angostas la bandeja y el lector se alternan
  const [isReaderOpen, setIsReaderOpen] = useState<boolean>(false);
  const [toast, setToast] = useState<ToastState | null>(null);

  const showToast = (message: string, tone: ToastState['tone'] = 'ok') =>
    setToast({ id: Date.now(), message, tone });
  const dismissToast = useCallback(() => setToast(null), []);

  const loadData = async (preserveSelected = true) => {
    setIsLoading(true);
    try {
      const [notifsData, statsData] = await Promise.all([
        fetchNotifications(selectedCategory, statusFilter, searchTerm),
        fetchStats(),
      ]);
      setNotifications(notifsData);
      setStats(statsData);

      const loadedThreads = groupThreads(notifsData);
      if (!preserveSelected || !selectedKey || !loadedThreads.find((t) => t.key === selectedKey)) {
        setSelectedKey(loadedThreads.length > 0 ? loadedThreads[0].key : null);
      }
    } catch (err) {
      console.error(err);
      showToast('No se pudieron cargar las notificaciones. Verifique que el servidor esté activo.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Los filtros recargan de inmediato; la búsqueda espera a que se deje de escribir
  const lastSearch = useRef(searchTerm);
  useEffect(() => {
    const searchChanged = lastSearch.current !== searchTerm;
    lastSearch.current = searchTerm;
    const timer = setTimeout(() => loadData(searchChanged), searchChanged ? 300 : 0);
    return () => clearTimeout(timer);
  }, [selectedCategory, statusFilter, searchTerm]);

  const threads = useMemo(() => groupThreads(notifications), [notifications]);
  const selectedThread = threads.find((t) => t.key === selectedKey) || null;

  const handleSelect = (key: string) => {
    setSelectedKey(key);
    setIsReaderOpen(true);
  };

  // Una sola decisión resuelve todos los correos pendientes del caso
  const handleSaveReview = async (review: HumanDecision, ids: string[]) => {
    setIsSaving(true);
    try {
      const updated = await submitHumanReviewBatch(ids, review);
      const byId = new Map(updated.map((n) => [n.id, n]));
      setNotifications((prev) => prev.map((n) => byId.get(n.id) ?? n));
      setStats(await fetchStats());
      showToast(
        ids.length > 1 ? `Decisión docente guardada para ${ids.length} correos del caso.` : 'Decisión docente guardada.'
      );
    } catch {
      showToast('No se pudo guardar la decisión. Intente de nuevo.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetSamples = async () => {
    setIsResetConfirmOpen(false);
    setIsLoading(true);
    try {
      const res = await resetSamples();
      await loadData(false);
      showToast(`Se restablecieron ${res.imported} notificaciones de muestra.`);
    } catch {
      showToast('No se pudieron restablecer los datos de muestra.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-canvas text-ink">
      <Navbar
        onOpenImport={() => setIsImportModalOpen(true)}
        onResetSamples={() => setIsResetConfirmOpen(true)}
        isLoading={isLoading}
      />

      <DashboardStats
        stats={stats}
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
      />

      <main className="flex min-h-0 flex-1">
        <section
          aria-label="Bandeja"
          className={`min-h-0 w-full shrink-0 sm:flex sm:w-96 md:w-[420px] ${isReaderOpen ? 'hidden' : 'flex'}`}
        >
          <div className="min-h-0 w-full">
            <NotificationList
              threads={threads}
              selectedKey={selectedKey}
              onSelect={handleSelect}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              statusFilter={statusFilter}
              onStatusFilterChange={setStatusFilter}
              isLoading={isLoading}
            />
          </div>
        </section>

        <section
          aria-label="Lector de mensaje"
          className={`min-h-0 min-w-0 flex-1 sm:flex ${isReaderOpen ? 'flex' : 'hidden'}`}
        >
          <NotificationDetail
            thread={selectedThread}
            onSaveReview={handleSaveReview}
            isSaving={isSaving}
            onBack={() => setIsReaderOpen(false)}
          />
        </section>
      </main>

      <ImportModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        onSuccess={() => {
          loadData(false);
          showToast('Notificación importada y analizada.');
        }}
      />

      <ConfirmDialog
        open={isResetConfirmOpen}
        title="¿Restaurar los casos de muestra?"
        description="Se reemplazarán las notificaciones actuales por los escenarios de demostración basados en las evidencias."
        confirmLabel="Restaurar casos"
        onConfirm={handleResetSamples}
        onCancel={() => setIsResetConfirmOpen(false)}
      />

      <Toast toast={toast} onDismiss={dismissToast} />
    </div>
  );
};
