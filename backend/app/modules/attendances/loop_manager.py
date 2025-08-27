from threading import Thread, Event
import queue
import asyncio

class LoopManager:
    def __init__(self, loop_func):
        """
        loop_func: función que recibe la instancia de LoopManager y se ejecuta en el hilo principal.
        """
        self.loop_func = loop_func
        self.running_event = Event()
        self.task_queue = queue.Queue()
        self._loop_thread = None
        self._worker_thread = None

    def start(self):
        """Inicia el loop principal y el worker asíncrono."""

        if self.is_running():
            print("El loop ya está ejecutándose.")
            return
        
        self.running_event.set()

        # Arranca el hilo worker asíncrono
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_thread = Thread(
                target=self._worker_async,
                daemon=True,
                name="WorkerAsync"
            )
            self._worker_thread.start()

        # Arranca el hilo principal con la función pasada
        if self._loop_thread is None or not self._loop_thread.is_alive():
            self._loop_thread = Thread(
                target=self.loop_func,
                daemon=True,
                name="LoopPrincipal"
            )
            self._loop_thread.start()

    def stop(self):
        """Detiene ambos hilos."""
        self.running_event.clear()

    def is_running(self):
        """Devuelve True si no se ha marcado stop_event."""
        return self.running_event.is_set()

    def delegar_async(self, coro_func, *args, **kwargs):
        """
        Encola una coroutine para ser ejecutada por el worker.
        coro_func: función async (no ejecutada todavía)
        """
        self.task_queue.put((coro_func, args, kwargs))

    def _worker_async(self):
        """Hilo dedicado a ejecutar coroutines en orden."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while not self.running_event.is_set():
            try:
                func, args, kwargs = self.task_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            loop.run_until_complete(func(*args, **kwargs))
            self.task_queue.task_done()