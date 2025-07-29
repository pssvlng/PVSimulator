import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ControlComponent } from './control.component';

describe('ControlComponent', () => {
  let component: ControlComponent;
  let fixture: ComponentFixture<ControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ControlComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ControlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should emit start event when start button clicked', () => {
    spyOn(component.start, 'emit');
    
    component.onStart();
    
    expect(component.start.emit).toHaveBeenCalled();
  });

  it('should emit stop event when stop button clicked', () => {
    spyOn(component.stop, 'emit');
    
    component.onStop();
    
    expect(component.stop.emit).toHaveBeenCalled();
  });

  it('should disable start button when simulation is running', () => {
    component.isRunning = true;
    fixture.detectChanges();
    
    const startButton = fixture.debugElement.nativeElement.querySelector('.btn-primary');
    expect(startButton.disabled).toBe(true);
  });

  it('should disable stop button when simulation is not running', () => {
    component.isRunning = false;
    fixture.detectChanges();
    
    const stopButton = fixture.debugElement.nativeElement.querySelector('.btn-danger');
    expect(stopButton.disabled).toBe(true);
  });
});
