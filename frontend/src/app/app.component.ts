import { Component, OnDestroy, OnInit } from '@angular/core';
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
  private pollingStop$ = new Subject<void>();
  private pollingInterval = 2000; // 2 seconds
  private maxDataPoints = 50; // Maximum number of data points to display
  private lastTimestamp = '';

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
    this.pollingStop$.next();
    this.pollingStop$.complete();
  }

  startSimulation(): void {
    console.log('Starting simulation...');
    this.error = null; // Clear any previous errors
    
    this.simulatorService.startSimulation()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('Start simulation response:', response);
          this.simulatorService.updateStatus(response.running);
          this.error = null;
        },
        error: (error) => {
          console.error('Start simulation error:', error);
          this.error = 'Failed to start simulation. Please check if the backend is running.';
          // Check current status to ensure UI is in sync
          this.simulatorService.checkCurrentStatus();
        }
      });
  }

  stopSimulation(): void {
    console.log('Stopping simulation...');
    // Immediately stop polling to prevent state conflicts
    this.stopPolling();
    
    this.simulatorService.stopSimulation()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('Stop simulation response:', response);
          this.simulatorService.updateStatus(response.running);
          this.error = null;
        },
        error: (error) => {
          console.error('Stop simulation error:', error);
          this.error = 'Failed to stop simulation.';
          // Even if the API call fails, refresh the status
          this.simulatorService.getStatus().subscribe(
            status => {
              console.log('Status refresh after stop error:', status);
              this.simulatorService.updateStatus(status.running);
            },
            err => console.error('Error refreshing status:', err)
          );
        }
      });
  }

  private startPolling(): void {
    // Stop any existing polling first
    this.pollingStop$.next();
    
    interval(this.pollingInterval)
      .pipe(
        takeUntil(this.destroy$),
        takeUntil(this.pollingStop$),
        switchMap(() => this.simulatorService.getLatestResults())
      )
      .subscribe({
        next: (data) => {
          this.updateChartData(data);
          this.error = null;
        },
        error: (error) => {
          console.error('Polling error:', error);
          this.error = 'Failed to fetch data from backend.';
        }
      });
  }

  private updateChartData(newData: SimulationData[]): void {
    if (!newData || newData.length === 0) {
      return;
    }

    // If this is the first data load or simulation was restarted, replace all data
    if (this.chartData.length === 0 || newData.length < this.maxDataPoints) {
      this.chartData = [...newData];
      this.lastTimestamp = newData[newData.length - 1]?.timestamp || '';
      this.latestData = newData[newData.length - 1] || null;
      return;
    }

    // Find new data points (timestamps newer than our last recorded timestamp)
    const newDataPoints = newData.filter(item => item.timestamp > this.lastTimestamp);
    
    if (newDataPoints.length > 0) {
      // Add new data points
      this.chartData = [...this.chartData, ...newDataPoints];
      
      // Keep only the latest maxDataPoints
      if (this.chartData.length > this.maxDataPoints) {
        this.chartData = this.chartData.slice(-this.maxDataPoints);
      }
      
      // Update last timestamp and latest data
      this.lastTimestamp = newDataPoints[newDataPoints.length - 1].timestamp;
      this.latestData = newDataPoints[newDataPoints.length - 1];
    }
  }

  private stopPolling(): void {
    this.pollingStop$.next();
  }

  private loadData(): void {
    this.simulatorService.getResults()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.chartData = data.slice(-this.maxDataPoints); // Keep only latest data
          this.lastTimestamp = this.chartData.length > 0 ? 
            this.chartData[this.chartData.length - 1].timestamp : '';
          this.latestData = this.chartData.length > 0 ? 
            this.chartData[this.chartData.length - 1] : null;
        },
        error: (error) => {
          console.error('Load data error:', error);
        }
      });
  }
}
