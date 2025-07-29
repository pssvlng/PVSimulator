import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { Subject, interval } from 'rxjs';
import { switchMap, takeUntil } from 'rxjs/operators';
import { SimulationData, SimulatorService } from './services/simulator.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  isRunning = false;
  chartData: SimulationData[] = [];
  latestData: SimulationData | null = null;
  error: string | null = null;
  private destroy$ = new Subject<void>();
  private pollingInterval = 2000; // 2 seconds
  private simulatorService = inject(SimulatorService);

  ngOnInit(): void {
    // Subscribe to status changes
    this.simulatorService.status$
      .pipe(takeUntil(this.destroy$))
      .subscribe(running => {
        this.isRunning = running;
        if (running) {
          this.startPolling();
        } else {
          this.stopPolling();
        }
      });

    // Initial data load
    this.loadData();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onStart(): void {
    this.startSimulation();
  }

  onStop(): void {
    this.stopSimulation();
  }

  startSimulation(): void {
    this.simulatorService.startSimulation()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.simulatorService.updateStatus(response.running);
          this.error = null;
        },
        error: (error) => {
          this.error = 'Failed to start simulation. Please check if the backend is running.';
          console.error('Start simulation error:', error);
        }
      });
  }

  stopSimulation(): void {
    this.simulatorService.stopSimulation()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.simulatorService.updateStatus(response.running);
          this.error = null;
        },
        error: (error) => {
          this.error = 'Failed to stop simulation.';
          console.error('Stop simulation error:', error);
        }
      });
  }

  private startPolling(): void {
    interval(this.pollingInterval)
      .pipe(
        takeUntil(this.destroy$),
        switchMap(() => this.simulatorService.getLatestResults())
      )
      .subscribe({
        next: (data) => {
          this.chartData = data;
          this.latestData = data.length > 0 ? data[data.length - 1] : null;
          this.error = null;
        },
        error: (error) => {
          console.error('Polling error:', error);
          this.error = 'Failed to fetch data from backend.';
        }
      });
  }

  private stopPolling(): void {
    // Polling stops automatically when destroy$ emits
  }

  private loadData(): void {
    this.simulatorService.getResults()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.chartData = data;
        },
        error: (error) => {
          console.error('Load data error:', error);
        }
      });
  }
}
