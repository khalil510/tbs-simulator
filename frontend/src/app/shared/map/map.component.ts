import { AfterViewInit, Component, effect, ElementRef, EventEmitter, input, Output, ViewChild } from '@angular/core';
import * as maplibregl from 'maplibre-gl';
import type { Map as MlMap } from 'maplibre-gl';
import { GeoJsonGeometry } from '../../core/models';

/**
 * MapLibre wrapper reused by planner / instructor / AAR views.
 * Uses OSM raster tiles (no API key). Swap for a vector tile provider
 * (MapTiler, Stadia) before production use.
 */
@Component({
  selector: 'tbs-map',
  standalone: true,
  template: `<div #container class="map"></div>`,
  styles: [`
    :host { display: block; width: 100%; height: 100%; }
    .map { width: 100%; height: 100%; }
  `],
})
export class MapComponent implements AfterViewInit {
  @ViewChild('container', { static: true }) container!: ElementRef<HTMLDivElement>;

  /** Clicks emit WGS84 lon/lat. */
  @Output() mapClick = new EventEmitter<{ lon: number; lat: number }>();

  aoi = input<GeoJsonGeometry | null>(null);
  markers = input<{ id: string; lon: number; lat: number; color: string }[]>([]);

  private map?: MlMap;

  constructor() {
    effect(() => {
      const geom = this.aoi();
      // The map may not exist yet; ngAfterViewInit also applies the value.
      queueMicrotask(() => this.setAoi(geom));
    });
  }

  ngAfterViewInit(): void {
    const map = new maplibregl.Map({
      container: this.container.nativeElement,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors',
          },
        },
        layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
      },
      center: [35.28, 31.81], // default AOI in the seed data (Israel-ish); change per use
      zoom: 11,
    });
    map.on('click', (e) => {
      this.mapClick.emit({ lon: e.lngLat.lng, lat: e.lngLat.lat });
    });
    this.map = map;
  }

  /** Add a temporary "place entity" vertex preview - called by planner. */
  addPreviewPoint(lon: number, lat: number, color = '#ffcc00'): void {
    if (!this.map) return;
    const el = document.createElement('div');
    el.style.width = '14px';
    el.style.height = '14px';
    el.style.borderRadius = '50%';
    el.style.border = '2px solid #fff';
    el.style.background = color;
    new maplibregl.Marker({ element: el }).setLngLat([lon, lat]).addTo(this.map);
  }

  flyTo(lon: number, lat: number, zoom = 12): void {
    this.map?.flyTo({ center: [lon, lat], zoom });
  }

  setAoi(geometry: GeoJsonGeometry | null): void {
    if (!this.map) return;
    const source = this.map.getSource('aoi') as maplibregl.GeoJSONSource | undefined;
    const data = geometry ? { type: 'Feature' as const, properties: {}, geometry } : { type: 'FeatureCollection' as const, features: [] };
    if (source) {
      source.setData(data as never);
      return;
    }
    if (geometry) {
      this.map.addSource('aoi', { type: 'geojson', data: data as never });
      this.map.addLayer({
        id: 'aoi-fill',
        type: 'fill',
        source: 'aoi',
        paint: { 'fill-color': '#3b82f6', 'fill-opacity': 0.12 },
      });
      this.map.addLayer({
        id: 'aoi-outline',
        type: 'line',
        source: 'aoi',
        paint: { 'line-color': '#3b82f6', 'line-width': 2 },
      });
    }
  }
}
