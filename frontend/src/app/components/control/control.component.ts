import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-control',
  template: `
    <div class="control-panel">
      <button 
        class="btn btn-primary" 
        (click)="onStart()" 
        [disabled]="isRunning">
        {{ isRunning ? 'Running...' : 'Start Simulation' }}
      </button>
      <button 
        class="btn btn-danger" 
        (click)="onStop()" 
        [disabled]="!isRunning">
        Stop Simulation
      </button>
    </div>
  `
})
export class ControlComponent {
  @Input() isRunning: boolean = false;
  @Output() start = new EventEmitter<void>();
  @Output() stop = new EventEmitter<void>();

  onStart(): void {
    this.start.emit();
  }

  onStop(): void {
    this.stop.emit();
  }
}
