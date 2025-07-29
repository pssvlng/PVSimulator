import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChartComponent } from './chart.component';

describe('ChartComponent', () => {
  let component: ChartComponent;
  let fixture: ComponentFixture<ChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ChartComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize chart on ngOnInit', () => {
    spyOn(component as any, 'initChart');
    
    component.ngOnInit();
    
    expect((component as any).initChart).toHaveBeenCalled();
  });

  it('should update chart when data changes', () => {
    spyOn(component as any, 'updateChart');
    
    component.data = [
      { timestamp: '2023-01-01T12:00:00', meter: 5.5, pv: 7.2, sum: 12.7 }
    ];
    component.ngOnChanges();
    
    expect((component as any).updateChart).toHaveBeenCalled();
  });

  it('should destroy chart on ngOnDestroy', () => {
    const mockChart = { destroy: jasmine.createSpy('destroy') };
    (component as any).chart = mockChart;
    
    component.ngOnDestroy();
    
    expect(mockChart.destroy).toHaveBeenCalled();
  });
});
