import { Component, ElementRef, Input, OnChanges, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Chart, ChartConfiguration, ChartOptions, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-chart',
  template: `
    <div class="chart-container">
      <canvas #chartCanvas></canvas>
    </div>
  `
})
export class ChartComponent implements OnInit, OnDestroy, OnChanges {
  @Input() data: any[] = [];
  @ViewChild('chartCanvas', { static: true }) chartCanvas!: ElementRef<HTMLCanvasElement>;
  
  private chart?: Chart;

  ngOnInit(): void {
    this.initChart();
  }

  ngOnDestroy(): void {
    if (this.chart) {
      this.chart.destroy();
    }
  }

  ngOnChanges(): void {
    if (this.chart && this.data) {
      this.updateChart();
    }
  }

  private initChart(): void {
    const ctx = this.chartCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Meter Consumption (kW)',
            data: [],
            borderColor: '#dc3545',
            backgroundColor: 'rgba(220, 53, 69, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          },
          {
            label: 'PV Production (kW)',
            data: [],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          },
          {
            label: 'Net Power (kW)',
            data: [],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'PV Simulator - Real-time Power Data'
          },
          legend: {
            display: true,
            position: 'top'
          }
        },
        scales: {
          x: {
            display: true,
            title: {
              display: true,
              text: 'Time'
            },
            ticks: {
              maxTicksLimit: 10 // Limit number of time labels to avoid crowding
            }
          },
          y: {
            display: true,
            title: {
              display: true,
              text: 'Power (kW)'
            },
            beginAtZero: true
          }
        },
        animation: {
          duration: 0 // Disable animations for better real-time performance
        },
        interaction: {
          intersect: false,
          mode: 'index'
        },
        elements: {
          point: {
            radius: 2, // Smaller points for cleaner look with many data points
            hoverRadius: 4
          }
        }
      } as ChartOptions
    };

    this.chart = new Chart(ctx, config);
    this.updateChart();
  }

  private updateChart(): void {
    if (!this.chart || !this.data) return;

    const labels = this.data.map(item => {
      const date = new Date(item.timestamp);
      return date.toLocaleTimeString();
    });

    // Update data efficiently
    this.chart.data.labels = labels;
    this.chart.data.datasets[0].data = this.data.map(item => item.meter);
    this.chart.data.datasets[1].data = this.data.map(item => item.pv);
    this.chart.data.datasets[2].data = this.data.map(item => item.sum);

    // Use 'none' animation mode for real-time updates to improve performance
    this.chart.update('none');
  }
}
