import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface SimulationData {
  timestamp: string;
  meter: number;
  pv: number;
  sum: number;
}

export interface SimulationStatus {
  running: boolean;
}

export interface SimulationResponse {
  status: string;
  running: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SimulatorService {
  private apiUrl = environment.production ? '/api' : 'http://localhost:5000';
  private statusSubject = new BehaviorSubject<boolean>(false);
  public status$ = this.statusSubject.asObservable();
  private http = inject(HttpClient);

  constructor() {
    this.checkStatus();
  }

  startSimulation(): Observable<SimulationResponse> {
    return this.http.post<SimulationResponse>(`${this.apiUrl}/start`, {});
  }

  stopSimulation(): Observable<SimulationResponse> {
    return this.http.post<SimulationResponse>(`${this.apiUrl}/stop`, {});
  }

  getStatus(): Observable<SimulationStatus> {
    return this.http.get<SimulationStatus>(`${this.apiUrl}/status`);
  }

  getResults(): Observable<SimulationData[]> {
    return this.http.get<SimulationData[]>(`${this.apiUrl}/results`);
  }

  getLatestResults(): Observable<SimulationData[]> {
    return this.http.get<SimulationData[]>(`${this.apiUrl}/results/latest`);
  }

  updateStatus(running: boolean): void {
    this.statusSubject.next(running);
  }

  private checkStatus(): void {
    this.getStatus().subscribe(
      status => this.statusSubject.next(status.running),
      error => console.error('Error checking status:', error)
    );
  }
}
