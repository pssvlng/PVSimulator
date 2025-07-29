import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { SimulationData, SimulationStatus, SimulatorService } from './simulator.service';

describe('SimulatorService', () => {
  let service: SimulatorService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [SimulatorService]
    });
    service = TestBed.inject(SimulatorService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should start simulation', () => {
    const mockResponse = { status: 'started', running: true };

    service.startSimulation().subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne('http://localhost:5000/start');
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('should stop simulation', () => {
    const mockResponse = { status: 'stopped', running: false };

    service.stopSimulation().subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne('http://localhost:5000/stop');
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('should get status', () => {
    const mockStatus: SimulationStatus = { running: true };

    service.getStatus().subscribe(status => {
      expect(status).toEqual(mockStatus);
    });

    const req = httpMock.expectOne('http://localhost:5000/status');
    expect(req.request.method).toBe('GET');
    req.flush(mockStatus);
  });

  it('should get results', () => {
    const mockData: SimulationData[] = [
      {
        timestamp: '2023-01-01T12:00:00',
        meter: 5.5,
        pv: 7.2,
        sum: 12.7
      }
    ];

    service.getResults().subscribe(data => {
      expect(data).toEqual(mockData);
    });

    const req = httpMock.expectOne('http://localhost:5000/results');
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('should get latest results', () => {
    const mockData: SimulationData[] = [
      {
        timestamp: '2023-01-01T12:00:00',
        meter: 5.5,
        pv: 7.2,
        sum: 12.7
      }
    ];

    service.getLatestResults().subscribe(data => {
      expect(data).toEqual(mockData);
    });

    const req = httpMock.expectOne('http://localhost:5000/results/latest');
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('should update status', () => {
    service.updateStatus(true);
    service.status$.subscribe(status => {
      expect(status).toBe(true);
    });
  });
});
