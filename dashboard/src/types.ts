// mirrors core/schemas.py

export interface SurfacePoint {
  expiry: string; // ISO 8601
  tte_years: number;
  delta: number;
  mark_iv: number;
  option_type: string;
}

export interface IVSurfaceResponse {
  currency: string;
  spot: number;
  as_of: string; // ISO 8601
  points: SurfacePoint[];
}
