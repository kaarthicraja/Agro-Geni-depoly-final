import React, { useState, useEffect } from "react";
import { 
  TrendingUp, 
  AlertTriangle, 
  Calendar, 
  ChevronRight, 
  ArrowUpRight, 
  ArrowDownRight,
  TrendingDown,
  Info,
  Cloud,
  AlertCircle
} from "lucide-react";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";
import { useLanguage } from "../LanguageContext";
import { t } from "../i18n";

export function AIInsights() {
  const { lang } = useLanguage();
  const [priceData, setPriceData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCrop, setSelectedCrop] = useState("wheat");
  const availableCrops = ["wheat", "rice", "tomato", "corn", "vegetables", "sugarcane", "cotton"];

  useEffect(() => {
    setLoading(true);
    // Fetch price forecast from backend
    fetch(`http://127.0.0.1:5000/api/ai/price-forecast?crop=${selectedCrop}`)
      .then(res => {
        if (!res.ok) throw new Error("Backend not responding");
        return res.json();
      })
      .then(data => {
        setError(null);
        // Format data for Recharts - data should be an array of forecast items
        const forecastArray = Array.isArray(data) ? data : (data.forecast || []);
        
        const formatted = forecastArray.map((item: any) => {
          // Handle both standard ISO strings and MongoDB-style {$date: ...} objects
          const rawDate = item.ds?.$date || item.ds || item.date;
          const dateObj = new Date(rawDate);
          
          // Check if date is valid
          if (isNaN(dateObj.getTime())) {
            console.warn("Invalid date:", rawDate);
            return null;
          }
          
          return {
            date: dateObj.toLocaleDateString(lang === 'ta' ? 'ta-IN' : 'en-IN', { day: 'numeric', month: 'short' }),
            price: Math.round(item.yhat || item.price || 0),
            lower: Math.round(item.yhat_lower || item.lower || 0),
            upper: Math.round(item.yhat_upper || item.upper || 0)
          };
        }).filter((item: any) => item !== null);
        
        if (formatted.length === 0) {
          setError("No forecast data available for the selected crop.");
        } else {
          setPriceData(formatted);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch AI data", err);
        setError("Unable to connect to AI Server. Please ensure the Python backend is running.");
        setLoading(false);
      });
  }, [lang, selectedCrop]);

  const stats = [
    { label: t('pricePrediction', lang), value: "+12.5%", trend: "up", icon: TrendingUp },
    { label: t('marketSentiment', lang), value: t('bullish', lang), trend: "up", icon: TrendingUp },
    { label: t('avgSpoilageRisk', lang), value: t('medium', lang), trend: "neutral", icon: AlertTriangle },
  ];

  return (
    <div className="p-6 md:p-10 bg-[#f9fafb] min-h-screen">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-primary" />
            {t('aiMarketInsights', lang)}
          </h1>
          <p className="text-muted-foreground text-lg">{t('predictiveAnalytics', lang)}</p>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {stats.map((stat, i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground font-medium mb-1">{stat.label}</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold">{stat.value}</span>
                  {stat.trend === "up" && <ArrowUpRight className="w-5 h-5 text-green-500" />}
                </div>
              </div>
              <div className="p-3 bg-primary/10 rounded-xl">
                <stat.icon className="w-6 h-6 text-primary" />
              </div>
            </div>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-white p-8 rounded-3xl border shadow-md">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="text-xl font-bold">{t('priceForecast30Days', lang)}</h3>
                <p className="text-sm text-muted-foreground">{t('predictedMovement', lang)}</p>
              </div>
              <div className="flex gap-2 flex-wrap">
                {availableCrops.map(crop => (
                  <button 
                    key={crop}
                    onClick={() => setSelectedCrop(crop)}
                    className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${selectedCrop === crop ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`}
                  >
                    {t(crop, lang)}
                  </button>
                ))}
              </div>
            </div>

            <div className="h-[400px] w-full">
              {loading ? (
                <div className="h-full w-full flex items-center justify-center bg-gray-50 rounded-xl">
                  <span className="animate-pulse text-primary font-medium">{t('analyzingTrends', lang)}</span>
                </div>
              ) : error ? (
                <div className="h-full w-full flex flex-col items-center justify-center bg-red-50 text-red-500 rounded-xl p-6 text-center border border-red-200">
                  <AlertCircle className="w-12 h-12 mb-3 opacity-80" />
                  <span className="font-bold text-lg mb-1">Server Disconnected</span>
                  <span className="text-sm opacity-80 max-w-sm">{error}</span>
                </div>
              ) : priceData && priceData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={priceData}>
                    <defs>
                      <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="date" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{fill: '#94a3b8', fontSize: 12}} 
                      dy={10}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{fill: '#94a3b8', fontSize: 12}} 
                      tickFormatter={(value) => `₹${value}`}
                    />
                    <Tooltip 
                      contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                      labelFormatter={(label) => `${t('date', lang)}: ${label}`}
                      formatter={(value: any) => [`₹${value}`, t('price', lang)]}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#22c55e" 
                      strokeWidth={3}
                      fillOpacity={1} 
                      fill="url(#colorPrice)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full w-full flex items-center justify-center bg-gray-50 rounded-xl">
                  <span className="text-gray-500">{lang === 'ta' ? 'தரவு கிடைக்கவில்லை' : 'No forecast data available'}</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-6">
            <div className="bg-white p-6 rounded-2xl border shadow-sm">
              <h4 className="font-bold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                {t('spoilageAlerts', lang)}
              </h4>
              <div className="space-y-4">
                <div className="p-4 bg-orange-50 border border-orange-100 rounded-xl">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-orange-900">{t('tomatoes', lang)} (Batch #42)</span>
                    <span className="text-xs bg-orange-200 px-2 py-0.5 rounded-full text-orange-900">3 {t('daysLeft', lang)}</span>
                  </div>
                  <p className="text-sm text-orange-800">{lang === 'ta' ? 'கிடங்கு A-வில் ஈரப்பதம் அதிகரித்து வருகிறது. நாளைக்குள் குளிர்சாதன கிடங்கிற்கு மாற்றவும்.' : 'Humidity at Godown A is rising. Move to cold storage by tomorrow.'}</p>
                </div>
                <div className="p-4 bg-red-50 border border-red-100 rounded-xl">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-red-900">{t('onions', lang)} (Batch #12)</span>
                    <span className="text-xs bg-red-200 px-2 py-0.5 rounded-full text-red-900">{t('critical', lang)}</span>
                  </div>
                  <p className="text-sm text-red-800">{lang === 'ta' ? 'வெப்பநிலை 32°C ஆக உள்ளது. 24 மணிநேரத்தில் அழுகும் என்று கணிக்கப்பட்டுள்ளது.' : 'Temperature detected at 32°C. Spoilage predicted in 24 hours.'}</p>
                </div>
              </div>
            </div>

            <div className="bg-primary p-6 rounded-2xl text-white shadow-lg overflow-hidden relative">
              <div className="relative z-10">
                <h4 className="font-bold text-lg mb-2">{t('maximizeProfit', lang)}</h4>
                <p className="text-primary-foreground text-sm mb-4">{lang === 'ta' ? 'அடுத்த வாரம் கோதுமை விலை 15% உயரும் என்று கணிக்கப்பட்டுள்ளது. உங்கள் இருப்பை இன்னும் 5 நாட்கள் வைத்திருக்கவும்.' : 'Wheat prices are predicted to hike by 15% next week. Hold your stock for 5 more days.'}</p>
                <button className="bg-white text-primary px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2">
                  {t('viewStrategy', lang)} <ChevronRight className="w-4 h-4" />
                </button>
              </div>
              <Cloud className="absolute -bottom-4 -right-4 w-24 h-24 opacity-20" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
