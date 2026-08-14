from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from .models import SaleAnalytics
from .serializers import SaleAnalyticsSerializer


class TrackSaleView(APIView):
    def post(self, request):
        serializer = SaleAnalyticsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalyticsSummaryView(APIView):
    def get(self, request):
        today = timezone.now().date()

        total_sales = SaleAnalytics.objects.count()
        total_revenue = (
            SaleAnalytics.objects.aggregate(total=Sum("total_price"))["total"] or 0
        )

        today_sales = SaleAnalytics.objects.filter(created_at__date=today).count()
        today_revenue = (
            SaleAnalytics.objects.filter(created_at__date=today).aggregate(
                total=Sum("total_price")
            )["total"]
            or 0
        )

        top_books = (
            SaleAnalytics.objects.values("book_title")
            .annotate(total_qty=Sum("quantity"))
            .order_by("-total_qty")[:3]
        )

        return Response(
            {
                "total_sales": total_sales,
                "total_revenue": float(total_revenue),
                "today_sales": today_sales,
                "today_revenue": float(today_revenue),
                "top_books": list(top_books),
            }
        )
