import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, interval } from 'rxjs';
import { switchMap, takeUntil } from 'rxjs/operators';
import { SimulationData, SimulatorService } from './services/simulator.service';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1>PV Simulator</h1>
      
      <div class="status-bar">
        <span 
          class="status-label"
          [ngClass]="isRunning ? 'status-running' : 'status-stopped'">
          {{ isRunning ? 'SIMULATION RUNNING' : 'SIMULATION STOPPED' }}
        </span>
      </div>

      <app-control 
        [isRunning]="isRunning"
        (start)="startSimulation()"
        (stop)="stopSimulation()">
      </app-control>

      <app-chart [data]="chartData"></app-chart>

      <div *ngIf="error" class="error">
        {{ error }}
      </div>
    </div>
  `
})
export class AppComponent implements OnInit, OnDestroy {
  isRunning = false;
  chartData: SimulationData[] = [];
  error: string | null = null;
  private destroy$ = new Subject<void>();
  private pollingInterval = 2000; // 2 seconds

  constructor(private simulatorService: SimulatorService) {}

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
