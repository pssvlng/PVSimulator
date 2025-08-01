import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ControlComponent } from './control.component';

describe('ControlComponent', () => {
  let component: ControlComponent;
  let fixture: ComponentFixture<ControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ControlComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ControlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with isRunning false', () => {
    expect(component.isRunning).toBeFalse();
  });

  it('should emit startEvent when onStart is called', () => {
    spyOn(component.startEvent, 'emit');
    
    component.onStart();
    
    expect(component.startEvent.emit).toHaveBeenCalled();
  });

  it('should emit stopEvent when onStop is called', () => {
    spyOn(component.stopEvent, 'emit');
    
    component.onStop();
    
    expect(component.stopEvent.emit).toHaveBeenCalled();
  });
});
