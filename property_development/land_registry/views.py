from django.contrib.gis.geos import Polygon
from django.shortcuts import render
from django.utils.dateparse import parse_date

from .models import PropertyProfile


def map_data_htmx_view(request):
    bbox = request.GET.get('bbox')

    if not bbox:
        return render(request, "_property_points.html", {'too_many': False, 'features': [], 'count': 0})

    try:
        sw_lng, sw_lat, ne_lng, ne_lat = map(float, bbox.split(','))
        bbox_poly = Polygon.from_bbox((sw_lng, sw_lat, ne_lng, ne_lat))
        bbox_poly.srid = 4326
    except Exception:
        return render(request, "_property_points.html", {'too_many': False, 'features': [], 'count': 0})

    qs = PropertyProfile.objects.filter(location__within=bbox_poly).select_related('land_registry_sale')

    # Optional filters
    min_price = request.GET.get("min_price")
    if min_price:
        qs = qs.filter(land_registry_sale__price_paid__gte=int(min_price))

    min_sqft = request.GET.get("min_sqft")
    if min_sqft:
        qs = qs.filter(price_per_sq_ft__gte=float(min_sqft))

    max_sqft = request.GET.get("max_sqft")
    if max_sqft:
        qs = qs.filter(price_per_sq_ft__lte=float(max_sqft))

    after_date = request.GET.get("after_date")
    if after_date:
        parsed_date = parse_date(after_date)
        if parsed_date:
            qs = qs.filter(land_registry_sale__deed_date__gte=parsed_date)

    count = qs.count()

    if count > 2000:
        return render(request, "_property_points.html", {'too_many': True, 'count': count})

    features = []
    for p in qs[:300]:
        if not p.location or not p.land_registry_sale:
            continue
        sale = p.land_registry_sale
        epc = p.epc_record

        address = f"{sale.full_address}, {sale.postcode}" or f"{sale.paon} {sale.street}, {sale.postcode}"
        floor_area_sqm = (
            f"{epc.total_floor_area:,.0f} m²" if epc and epc.total_floor_area else "N/A"
        )
        floor_area_sqft = (
            f"{float(epc.total_floor_area) * 10.7639:,.0f} sqft"
            if epc and epc.total_floor_area
            else "N/A"
        )
        hab_rooms = epc.number_habitable_rooms if epc and epc.number_habitable_rooms else "N/A"
        price_sqft = f"{p.price_per_sq_ft:,.0f}" if p.price_per_sq_ft else "N/A"
        price_sqm = f"{p.price_per_sq_metre:,.0f}" if p.price_per_sq_metre else "N/A"

        label = (
            f"<div class='text-sm leading-tight'>"
            f"<div class='font-bold text-base text-gray-900'>{address}</div>"
            f"<div class='text-gray-700'>£{sale.price_paid:,} — {sale.deed_date}</div>"
            f"<div>{p.estimated_num_bedrooms or '?'} beds "
            f"— <span class='font-medium'>£{price_sqft}/sqft</span> "
            f"— <span class='font-medium'>£{price_sqm}/m²</span></div>"
            f"<div class='text-gray-600'>Area: {floor_area_sqft} — {floor_area_sqm}</div>"
            f"<div class='text-gray-600'>Habitable Rooms: {hab_rooms}</div>"
            f"</div>"
        )


        features.append({
            'id': p.id,
            'lat': p.location.y,
            'lng': p.location.x,
            'label': label,
        })

    return render(request, "_property_points.html", {
        'too_many': False,
        'features': features,
        'count': count
    })
